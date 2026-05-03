import contractor1 from "@/assets/contractor-1.jpg";
import contractor2 from "@/assets/contractor-2.jpg";
import contractor3 from "@/assets/contractor-3.jpg";
import contractor4 from "@/assets/contractor-4.jpg";
import contractor5 from "@/assets/contractor-5.jpg";
import contractor6 from "@/assets/contractor-6.jpg";

export type ContractorSpecialty =
  | "General Contractor"
  | "Architect"
  | "Interior Design"
  | "Landscaping"
  | "Renovation"
  | "Electrical"
  | "Plumbing"
  | "Roofing";

export interface Contractor {
  id: string;
  name: string;
  avatarUrl: string;
  specialty: ContractorSpecialty;
  location: string;
  rating: number; // 0–5
  reviewCount: number;
  yearsExperience: number;
  hourlyRate: number;
  verified: boolean;
  bio: string;
  tags: string[];
}

export const contractors: Contractor[] = [
  {
    id: "c-001",
    name: "Marcus Reyes",
    avatarUrl: contractor1,
    specialty: "General Contractor",
    location: "Austin, TX",
    rating: 4.9,
    reviewCount: 184,
    yearsExperience: 12,
    hourlyRate: 95,
    verified: true,
    bio: "Full-service residential builder specializing in modern custom homes and additions.",
    tags: ["Custom Homes", "Additions", "Permitting"],
  },
  {
    id: "c-002",
    name: "Elena Park",
    avatarUrl: contractor2,
    specialty: "Architect",
    location: "Seattle, WA",
    rating: 4.8,
    reviewCount: 96,
    yearsExperience: 15,
    hourlyRate: 140,
    verified: true,
    bio: "Award-winning architect focused on sustainable, light-filled residential design.",
    tags: ["Sustainable", "Modern", "ADUs"],
  },
  {
    id: "c-003",
    name: "Cole Whitaker",
    avatarUrl: contractor3,
    specialty: "Renovation",
    location: "Denver, CO",
    rating: 4.7,
    reviewCount: 143,
    yearsExperience: 18,
    hourlyRate: 85,
    verified: true,
    bio: "Whole-home renovation expert. Kitchens, baths, and structural updates done right.",
    tags: ["Kitchen", "Bath", "Structural"],
  },
  {
    id: "c-004",
    name: "Priya Anand",
    avatarUrl: contractor4,
    specialty: "General Contractor",
    location: "San Diego, CA",
    rating: 4.9,
    reviewCount: 212,
    yearsExperience: 10,
    hourlyRate: 110,
    verified: true,
    bio: "Commercial-grade project management for ambitious residential builds.",
    tags: ["PM", "Commercial", "Smart Home"],
  },
  {
    id: "c-005",
    name: "Diego Romero",
    avatarUrl: contractor5,
    specialty: "Landscaping",
    location: "Phoenix, AZ",
    rating: 4.6,
    reviewCount: 78,
    yearsExperience: 8,
    hourlyRate: 65,
    verified: false,
    bio: "Drought-tolerant landscape design with a focus on outdoor living spaces.",
    tags: ["Xeriscape", "Patios", "Irrigation"],
  },
  {
    id: "c-006",
    name: "Hannah Liu",
    avatarUrl: contractor6,
    specialty: "Interior Design",
    location: "Brooklyn, NY",
    rating: 4.8,
    reviewCount: 134,
    yearsExperience: 9,
    hourlyRate: 120,
    verified: true,
    bio: "Editorial interiors balancing warmth, texture, and timeless materiality.",
    tags: ["Editorial", "Warm Modern", "Color"],
  },
  {
    id: "c-007",
    name: "Owen Bradley",
    avatarUrl: contractor1,
    specialty: "Roofing",
    location: "Portland, OR",
    rating: 4.5,
    reviewCount: 62,
    yearsExperience: 14,
    hourlyRate: 75,
    verified: true,
    bio: "Metal and composite roofing built to handle the Pacific Northwest.",
    tags: ["Metal", "Composite", "Repairs"],
  },
  {
    id: "c-008",
    name: "Sofia Marquez",
    avatarUrl: contractor4,
    specialty: "Electrical",
    location: "Miami, FL",
    rating: 4.7,
    reviewCount: 101,
    yearsExperience: 11,
    hourlyRate: 90,
    verified: true,
    bio: "Licensed master electrician. Panels, EV chargers, and full rewires.",
    tags: ["EV", "Panels", "Smart"],
  },
  {
    id: "c-009",
    name: "Jonas Becker",
    avatarUrl: contractor3,
    specialty: "Plumbing",
    location: "Chicago, IL",
    rating: 4.4,
    reviewCount: 54,
    yearsExperience: 16,
    hourlyRate: 80,
    verified: false,
    bio: "Repipes, tankless installs, and emergency service across Chicagoland.",
    tags: ["Tankless", "Repipe", "Emergency"],
  },
];

export const SPECIALTIES: ContractorSpecialty[] = [
  "General Contractor",
  "Architect",
  "Interior Design",
  "Renovation",
  "Landscaping",
  "Electrical",
  "Plumbing",
  "Roofing",
];

export const LOCATIONS = Array.from(
  new Set(contractors.map((c) => c.location))
).sort();
