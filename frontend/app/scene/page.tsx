"use client";

import dynamic from "next/dynamic";

// The Vestaboard library accesses window when its module is loaded.
const ScenePage = dynamic(() => import("@/components/ScenePage"), {
  ssr: false,
});

export default ScenePage;
