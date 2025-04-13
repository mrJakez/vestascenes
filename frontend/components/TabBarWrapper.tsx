"use client";

import { useState, useEffect } from "react";
import { TabBar } from "@vestaboard/installables";

interface TabBarWrapperProps {
  onChange?: (val: number) => void;
}

export default function TabBarWrapper({ onChange }: TabBarWrapperProps) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (onChange) onChange(value);
  }, [value, onChange]);

  return (
    <TabBar
      disableRipple={false}
      fullWidth={true}
      value={value}
      setValue={setValue}
      tabs={[
          { key: "history", label: "History" },
          { key: "scenes", label: "Scenes" },
          { key: "editor", label: "Editor" }
      ]}
    />
  );
}