export interface Planet {
  name: string;
  longitude: number;
  latitude: number;
  distance: number;
  speed: number;
  house: number;
  sign: string;
  aspectDegree: number;
  isRetrograde: boolean;
}

export interface House {
  number: number;
  cusp: number;
  sign: string;
}

export interface Aspect {
  planet1: string;
  planet2: string;
  type: string;
  orb: number;
  exactitude: number;
  nature: 'harmonious' | 'challenging' | 'neutral';
}

export interface BirthChart {
  planets: Planet[];
  houses: House[];
  aspects: Aspect[];
  angles: {
    ascendant: number;
    midheaven: number;
    descendant: number;
    imumCoeli: number;
  };
  lunarPhase: {
    phase: string;
    illumination: number;
    age: number;
  };
  points: {
    northNode: number;
    southNode: number;
    partOfFortune: number;
    vertex: number;
  };
}

export interface MoonInfo {
  phase: string;
  illumination: number;
  age: number;
  distance: number;
  nextNewMoon: string;
  nextFullMoon: string;
  mansion: {
    number: number;
    name: string;
    symbol: string;
  };
}

export interface StarPosition {
  name: string;
  constellation: string;
  magnitude: number;
  longitude: number;
  latitude: number;
  isVisible: boolean;
}

export interface Transit {
  planet: string;
  entryTime: string;
  exitTime: string;
  sign: string;
  house: number;
  aspects: Aspect[];
}

export interface Dignity {
  planet: string;
  essential: {
    ruler: boolean;
    exaltation: boolean;
    detriment: boolean;
    fall: boolean;
    score: number;
  };
  accidental: {
    house: number;
    speed: number;
    angularity: number;
    score: number;
  };
}

export interface Pattern {
  type: string;
  planets: string[];
  quality: string;
  power: number;
}

export interface TimingTechnique {
  type: 'solar_return' | 'lunar_return' | 'profection' | 'progression' | 'direction';
  date: string;
  significantPlanets: Planet[];
  interpretation: string;
}

export interface PredictiveEvent {
  type: string;
  startDate: string;
  endDate: string;
  planets: string[];
  nature: string;
  significance: number;
  description: string;
}
