import { FlatCompat } from "@eslint/eslintrc";
import { dirname } from "path";
import { fileURLToPath } from "url";
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname
});

const eslintConfig = [
  ...nextCoreWebVitals,
  ...nextTypescript,
  ...compat.config({
    extends: [
      "prettier",
      "plugin:prettier/recommended"
    ],
    plugins: ["simple-import-sort"],
    rules: {
      "prefer-arrow-callback": "error",
      "no-console": ["error", { allow: ["warn", "error"] }],
      semi: ["error", "always"],
      quotes: ["error", "double"],
      "react/jsx-uses-react": "off",
      "react/react-in-jsx-scope": "off",
      "react/no-children-prop": "error",
      "no-extra-boolean-cast": "error",
      "prefer-const": "error",
      "no-var": "error",
      "import/order": [
        "error",
        {
          groups: [
            ["builtin", "external"],
            ["internal"],
            ["parent", "sibling", "index"]
          ],
          "newlines-between": "always"
        }
      ]
    }
  })
];

export default eslintConfig;
