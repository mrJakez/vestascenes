import type { NextConfig } from "next";
import type { RuleSetRule } from "webpack";

const nextConfig: NextConfig = {
  output: "standalone",
  webpack: (config) => {
    const imageRule = config.module.rules.find(
      (rule: RuleSetRule): rule is RuleSetRule =>
        typeof rule === "object" &&
        rule !== null &&
        "test" in rule &&
        rule.test instanceof RegExp &&
        rule.test.test(".svg")
    );

    if (imageRule) {
      // exclude SVGs from the default Next.js image loader
      imageRule.exclude = [/\.svg$/, /\.png$/];
    }

    config.module.rules.push(
      {
        test: /\.svg$/,
        type: "asset/resource",
      },
      {
        test: /\.png$/,
        type: "asset/resource",
      }
    );

    return config;
  },
};

export default nextConfig;