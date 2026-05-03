import portfolio1 from "@/assets/portfolio-1.jpg";
import portfolio2 from "@/assets/portfolio-2.jpg";
import portfolio3 from "@/assets/portfolio-3.jpg";
import portfolio4 from "@/assets/portfolio-4.jpg";

export interface PortfolioItem {
  id: string;
  title: string;
  category: string;
  imageUrl: string;
}

export interface Review {
  id: string;
  author: string;
  rating: number;
  date: string; // ISO
  body: string;
}

// Shared portfolio pool — every contractor surfaces a curated subset.
export const PORTFOLIO_POOL: PortfolioItem[] = [
  { id: "p1", title: "Hillside Kitchen Remodel", category: "Kitchen", imageUrl: portfolio1 },
  { id: "p2", title: "Cedar Modern Residence",   category: "New Build", imageUrl: portfolio2 },
  { id: "p3", title: "Spa Master Bath",          category: "Bath",      imageUrl: portfolio3 },
  { id: "p4", title: "Vaulted Great Room",       category: "Renovation",imageUrl: portfolio4 },
  { id: "p5", title: "Garden Pavilion",          category: "Exterior",  imageUrl: portfolio2 },
  { id: "p6", title: "Walnut Galley Kitchen",    category: "Kitchen",   imageUrl: portfolio1 },
];

export const SAMPLE_REVIEWS: Review[] = [
  {
    id: "r1",
    author: "Aisha N.",
    rating: 5,
    date: "2026-02-14",
    body: "Communicative, on time, and meticulous. Our kitchen came in $4k under budget.",
  },
  {
    id: "r2",
    author: "Tom B.",
    rating: 5,
    date: "2026-01-22",
    body: "The crew treated our home like their own. Punch list was zero by walkthrough.",
  },
  {
    id: "r3",
    author: "Lena O.",
    rating: 4,
    date: "2025-11-30",
    body: "Beautiful work. A small delay on cabinetry but they kept us informed daily.",
  },
  {
    id: "r4",
    author: "Marco D.",
    rating: 5,
    date: "2025-10-08",
    body: "Best contractor experience we've had. Hire them before someone else does.",
  },
];
