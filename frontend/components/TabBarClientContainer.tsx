"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import Editor from "@/components/BoardEditor";
import invariant from "tiny-invariant";
import {HistoryContainer} from "@/components/HistoryContainer"
import {ScenesContainer} from "@/components/ScenesContainer"

// Dynamisch laden
const TabBarWrapper = dynamic(() => import("./TabBarWrapper"), {
  ssr: false,
});


export default function TabBarClientContainer() {
  const [tabIndex, setTabIndex] = useState(0);
  invariant(process.env.NEXT_PUBLIC_BACKEND_URL, "BACKEND_URL is required");

  return (
	<div>
	  <TabBarWrapper onChange={setTabIndex} />

	  <div style={{ marginTop: "1rem" }}>
          {tabIndex === 0 && <div>
              <HistoryContainer />
          </div>}
          {tabIndex === 1 && <div>
              <ScenesContainer />
          </div>}
          {tabIndex === 2 && <div>
              <Editor backendUrl={process.env.NEXT_PUBLIC_BACKEND_URL} />
          </div>}
	  </div>
	</div>
  );
}