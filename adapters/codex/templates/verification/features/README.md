# Feature verification map

Keep one concise Markdown file per important user or API path. Name each file with a stable feature ID, such as `sign-in.md`, and describe the behavior an independent Tester can observe.

Each completed feature document should state its preconditions, launch/readiness instructions, actions, expected results, evidence to capture, and cleanup. Prefer commands and fixtures already supported by the product repository. Refer to test accounts by an existing secret-manager name or fixture; never write credential values here.

Copy `feature.template.md` to a new feature file and replace every placeholder before using it. The template itself is not a feature and must never be counted as verified coverage.
