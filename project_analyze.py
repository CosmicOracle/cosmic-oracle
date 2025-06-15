#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import re
from datetime import datetime
import hashlib
from pathlib import Path
import mimetypes
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProjectAnalyzer:
    def __init__(self, root_dir='.', exclude_dirs=None, exclude_files=None, max_file_size=1000000):
        self.root_dir = os.path.abspath(root_dir)
        self.exclude_dirs = exclude_dirs or ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build']
        self.exclude_files = exclude_files or ['.DS_Store', '.env', '.gitignore']
        self.max_file_size = max_file_size
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'file_types': {},
            'language_stats': {},
            'largest_files': [],
            'newest_files': [],
            'scripts': [],
            'dependencies': {}
        }

        # Set up file type mapping
        self.language_extensions = {
            'python': ['.py', '.pyw', '.pyx', '.pyi'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'typescript': ['.ts', '.tsx'],
            'html': ['.html', '.htm'],
            'css': ['.css'],
            'java': ['.java'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.cc', '.cxx', '.hpp'],
            'rust': ['.rs'],
            'go': ['.go'],
            'ruby': ['.rb'],
            'php': ['.php'],
            'shell': ['.sh', '.bash'],
            'markdown': ['.md', '.markdown'],
            'json': ['.json'],
            'yaml': ['.yml', '.yaml']
        }

    def analyze(self):
        logging.info(f"Starting analysis of project: {os.path.basename(self.root_dir)}")
        logging.info(f"Project root: {self.root_dir}")

        try:
            # Analyze project structure
            self._scan_directory(self.root_dir)

            # Detect dependency files
            self._detect_dependencies()

            # Detect executable scripts
            self._detect_scripts()

            # Generate and print report
            report = self._generate_report()
            logging.info("Analysis completed successfully.")
            return report

        except Exception as e:
            logging.error(f"An error occurred during analysis: {e}", exc_info=True)
            raise

    def _scan_directory(self, directory):
        logging.debug(f"Scanning directory: {directory}")
        for root, dirs, files in os.walk(directory):
            # Filter excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            # Count directories
            self.stats['total_dirs'] += len(dirs)

            # Process files
            for file in files:
                if file in self.exclude_files:
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.root_dir)

                try:
                    # Get file stats
                    file_stats = os.stat(file_path)
                    file_size = file_stats.st_size
                    mod_time = file_stats.st_mtime

                    # Skip large files
                    if file_size > self.max_file_size:
                        logging.warning(f"Skipping large file: {rel_path} ({self._format_size(file_size)})")
                        continue

                    # Update file counts and sizes
                    self.stats['total_files'] += 1
                    self.stats['total_size'] += file_size

                    # Track file types
                    ext = os.path.splitext(file.lower())[1]
                    if ext:
                        self.stats['file_types'][ext] = self.stats['file_types'].get(ext, 0) + 1

                        # Update language stats
                        for lang, extensions in self.language_extensions.items():
                            if ext in extensions:
                                self.stats['language_stats'][lang] = self.stats['language_stats'].get(lang, 0) + 1
                                break

                    # Track largest files
                    self.stats['largest_files'].append((rel_path, file_size))
                    self.stats['largest_files'] = sorted(self.stats['largest_files'],
                                                        key=lambda x: x[1],
                                                        reverse=True)[:10]

                    # Track newest files
                    self.stats['newest_files'].append((rel_path, mod_time))
                    self.stats['newest_files'] = sorted(self.stats['newest_files'],
                                                      key=lambda x: x[1],
                                                      reverse=True)[:10]

                except Exception as e:
                    logging.error(f"Error processing file {rel_path}: {str(e)}", exc_info=True)

    def _detect_dependencies(self):
        # Python dependencies
        if os.path.exists(os.path.join(self.root_dir, 'requirements.txt')):
            self.stats['dependencies']['python'] = self._parse_requirements_txt()

        # Node.js dependencies
        if os.path.exists(os.path.join(self.root_dir, 'package.json')):
            self.stats['dependencies']['nodejs'] = self._parse_package_json()

        # Other dependency files to check
        dep_files = {
            'go': 'go.mod',
            'rust': 'Cargo.toml',
            'java': 'pom.xml',
            'ruby': 'Gemfile'
        }

        for lang, file_name in dep_files.items():
            if os.path.exists(os.path.join(self.root_dir, file_name)):
                self.stats['dependencies'][lang] = f"Found {file_name} (detailed parsing not implemented)"

    def _parse_requirements_txt(self):
        try:
            req_path = os.path.join(self.root_dir, 'requirements.txt')
            dependencies = []
            with open(req_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dependencies.append(line)
            return dependencies
        except FileNotFoundError:
            logging.warning("requirements.txt not found.")
            return []
        except Exception as e:
            logging.error(f"Error parsing requirements.txt: {e}", exc_info=True)
            return f"Error parsing requirements.txt: {str(e)}"

    def _parse_package_json(self):
        try:
            pkg_path = os.path.join(self.root_dir, 'package.json')
            with open(pkg_path, 'r') as f:
                data = json.load(f)

            deps = {}
            if 'dependencies' in data:
                deps['dependencies'] = list(data['dependencies'].keys())
            if 'devDependencies' in data:
                deps['devDependencies'] = list(data['devDependencies'].keys())

            return deps
        except FileNotFoundError:
            logging.warning("package.json not found.")
            return {}
        except Exception as e:
            logging.error(f"Error parsing package.json: {e}", exc_info=True)
            return f"Error parsing package.json: {str(e)}"

    def _detect_scripts(self):
        # Check for package.json scripts
        if os.path.exists(os.path.join(self.root_dir, 'package.json')):
            try:
                with open(os.path.join(self.root_dir, 'package.json'), 'r') as f:
                    data = json.load(f)
                    if 'scripts' in data:
                        for name, cmd in data['scripts'].items():
                            self.stats['scripts'].append({
                                'name': name,
                                'command': cmd,
                                'type': 'npm'
                            })
            except Exception as e:
                logging.error(f"Error parsing package.json scripts: {str(e)}", exc_info=True)

        # Check for executable scripts
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.root_dir)

                # Skip excluded directories
                if any(excluded in file_path for excluded in self.exclude_dirs):
                    continue

                try:
                    # Check if file is executable
                    is_executable = os.access(file_path, os.X_OK)

                    if is_executable:
                        script_type = self._detect_script_type(file_path)
                        if script_type:
                            self.stats['scripts'].append({
                                'name': rel_path,
                                'type': script_type,
                                'executable': True
                            })
                except Exception as e:
                    logging.error(f"Error checking script {rel_path}: {str(e)}", exc_info=True)

    def _detect_script_type(self, file_path):
        ext = os.path.splitext(file_path.lower())[1]

        if ext in ['.py']:
            return 'python'
        elif ext in ['.js', '.mjs']:
            return 'javascript'
        elif ext in ['.sh', '.bash']:
            return 'shell'
        elif ext in ['.rb']:
            return 'ruby'
        elif ext in ['.php']:
            return 'php'

        # Check shebang line for scripts without extension
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    if 'python' in first_line:
                        return 'python'
                    elif 'node' in first_line:
                        return 'javascript'
                    elif any(shell in first_line for shell in ['bash', 'sh', 'zsh']):
                        return 'shell'
                    elif 'ruby' in first_line:
                        return 'ruby'
                    elif 'php' in first_line:
                        return 'php'
                    else:
                        return 'unknown'
        except Exception:
            pass

        return None

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def _format_timestamp(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def _generate_report(self):
        report = {}

        report["general_statistics"] = {
            "total_directories": self.stats['total_dirs'],
            "total_files": self.stats['total_files'],
            "total_size": self._format_size(self.stats['total_size'])
        }

        language_stats = []
        for lang, count in sorted(self.stats['language_stats'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_files']) * 100
            language_stats.append({"language": lang, "count": count, "percentage": f"{percentage:.1f}%"})
        report["language_statistics"] = language_stats

        file_types = []
        for ext, count in sorted(self.stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:15]:
            file_types.append({"extension": ext, "count": count})
        report["file_types"] = file_types

        largest_files = []
        for path, size in self.stats['largest_files']:
            largest_files.append({"path": path, "size": self._format_size(size)})
        report["largest_files"] = largest_files

        newest_files = []
        for path, timestamp in self.stats['newest_files']:
            newest_files.append({"path": path, "last_modified": self._format_timestamp(timestamp)})
        report["newest_files"] = newest_files

        dependencies = {}
        for lang, deps in self.stats['dependencies'].items():
            lang_deps = [] # Reset this for each language.
            if isinstance(deps, list):
                lang_deps = deps[:10]  # Store the dependencies list
                if len(deps) > 10:
                    lang_deps.append(f"... and {len(deps) - 10} more")
            elif isinstance(deps, dict):
                lang_deps = {}  # Create a dictionary to store dep types
                for dep_type, dep_list in deps.items():
                    type_deps = dep_list[:10]
                    if len(dep_list) > 10:
                        type_deps.append(f"... and {len(dep_list) - 10} more")
                    lang_deps[dep_type] = type_deps  # Store the deps by type
            else:
                lang_deps = deps
            dependencies[lang] = lang_deps
        report["dependencies"] = dependencies

        scripts = {}
        npm_scripts = [s for s in self.stats['scripts'] if s.get('type') == 'npm']
        other_scripts = [s for s in self.stats['scripts'] if s.get('type') != 'npm']

        if npm_scripts:
            npm_script_list = []
            for script in npm_scripts[:15]:
                npm_script_list.append({"name": script['name'], "command": script['command']})
            if len(npm_scripts) > 15:
                npm_script_list.append(f"... and {len(npm_scripts) - 15} more")
            scripts["npm_scripts"] = npm_script_list

        if other_scripts:
            other_script_list = []
            for script in other_scripts[:15]:
                other_script_list.append({"name": script['name'], "type": script['type']})
            if len(other_scripts) > 15:
                other_script_list.append(f"... and {len(other_scripts) - 15} more")
            scripts["executable_scripts"] = other_script_list
        report["scripts"] = scripts

        # Project structure tree
        try:
            structure = self._get_directory_tree(self.root_dir, max_depth=3)
            report["project_structure"] = structure
        except Exception as e:
            logging.error(f"Error generating directory tree: {str(e)}", exc_info=True)
            report["project_structure"] = f"Error generating directory tree: {str(e)}"

        return report

    def _get_directory_tree(self, start_path, max_depth=3):
        if not os.path.isdir(start_path):
            return None

        tree = {}
        items = os.listdir(start_path)
        items = [item for item in items if item not in self.exclude_dirs and item not in self.exclude_files]
        items.sort()

        for item in items:
            item_path = os.path.join(start_path, item)
            if os.path.isdir(item_path):
                subtree = self._get_directory_tree(item_path, max_depth - 1)
                if subtree is not None:
                    tree[item + '/'] = subtree
            else:
                tree[item] = None

        return tree

    def print_report(self, report):
        """Prints the formatted report to the console."""
        print("\n" + "=" * 80)
        print("PROJECT ANALYSIS REPORT")
        print("=" * 80)

        # Basic stats
        print("\nGENERAL STATISTICS:")
        print(f"  • Total directories: {report['general_statistics']['total_directories']}")
        print(f"  • Total files: {report['general_statistics']['total_files']}")
        print(f"  • Total size: {report['general_statistics']['total_size']}")

        # Language stats
        if report.get('language_statistics'):
            print("\nLANGUAGE STATISTICS:")
            for lang_info in report['language_statistics']:
                print(f"  • {lang_info['language']}: {lang_info['count']} files ({lang_info['percentage']})")

        # File types
        if report.get('file_types'):
            print("\nFILE TYPES:")
            for file_type in report['file_types']:
                print(f"  • {file_type['extension']}: {file_type['count']} files")

        # Largest files
        if report.get('largest_files'):
            print("\nLARGEST FILES:")
            for file_info in report['largest_files']:
                print(f"  • {file_info['path']} ({file_info['size']})")

        # Newest files
        if report.get('newest_files'):
            print("\nMOST RECENTLY MODIFIED FILES:")
            for file_info in report['newest_files']:
                print(f"  • {file_info['path']} ({file_info['last_modified']})")

        # Dependencies
        if report.get('dependencies'):
            print("\nDEPENDENCIES:")
            for lang, deps in report['dependencies'].items():
                print(f"  • {lang.upper()}:")
                if isinstance(deps, list):
                    for dep in deps:
                        print(f"    - {dep}")
                elif isinstance(deps, dict):
                    for dep_type, dep_list in deps.items():
                        print(f"    {dep_type}:")
                        for dep in dep_list:
                            print(f"      - {dep}")
                else:
                    print(f"    {deps}")

        # Scripts
        if report.get('scripts'):
            print("\nSCRIPTS:")
            for script_type, script_list in report['scripts'].items():
                print(f"  • {script_type.upper().replace('_', ' ')}:")
                if isinstance(script_list, list):
                    for script in script_list:
                        if isinstance(script, dict):
                            print(f"    - {script['name']}: {script.get('command', '')}")
                        else:
                            print(f"    - {script}")

        # Project structure
        if report.get('project_structure'):
            print("\nPROJECT STRUCTURE:")
            self._print_directory_structure(report['project_structure'])

        print("\n" + "=" * 80)
        print(f"ANALYSIS COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")

    def _print_directory_structure(self, structure, prefix=''):
        """Prints the project structure from the nested dictionary."""
        for item, subtree in sorted(structure.items()):
            if subtree is None:  # It's a file
                print(f"{prefix}└── {item}")
            else:  # It's a directory
                print(f"{prefix}├── {item}")
                self._print_directory_structure(subtree, prefix + "│   ")

def main():
    parser = argparse.ArgumentParser(description='Analyze project structure and generate a comprehensive report')
    parser.add_argument('--dir', '-d', default='.', help='Project root directory (default: current directory)')
    parser.add_argument('--exclude-dirs', '-ed', nargs='*', help='Additional directories to exclude')
    parser.add_argument('--exclude-files', '-ef', nargs='*', help='Additional files to exclude')
    parser.add_argument('--max-file-size', '-m', type=int, default=1000000,
                      help='Maximum file size to analyze in bytes (default: 1MB)')
    parser.add_argument('--output', '-o', help='Output file for JSON report')
    args = parser.parse_args()

    # Get additional excludes
    exclude_dirs = ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build']
    if args.exclude_dirs:
        exclude_dirs.extend(args.exclude_dirs)

    exclude_files = ['.DS_Store', '.env', '.gitignore']
    if args.exclude_files:
        exclude_files.extend(args.exclude_files)

    # Create analyzer
    analyzer = ProjectAnalyzer(
        root_dir=args.dir,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        max_file_size=args.max_file_size
    )

    try:
        # Run analysis
        report = analyzer.analyze()

        # Print report to console
        analyzer.print_report(report)

        # Output JSON if requested
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2)
                logging.info(f"JSON report saved to: {args.output}")
            except Exception as e:
                logging.error(f"Error saving JSON report: {str(e)}", exc_info=True)

    except Exception as e:
        logging.error(f"An error occurred during the analysis: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
