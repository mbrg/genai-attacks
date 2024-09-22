# Welcome to GenAI Attacks Matrix!

## What To Expect

| :flashlight: | A community-driven knowledge source about TTPs adversaries can and do use to target GenAI-based systems including copilots and agents |
|------|:---|

GenAI is being applied to every imaginable problem within the world's largest businesses today, which we all rely on. We're all moving as fast as possible to adopt AI and reap its benefits first. Companies are adopting AI platforms, customizing them and building their own. In parallel, it's become increasingly clear that we don't yet know how to build secure systems with GenAI. Fresh research is coming out every week on new attack techniques, models and their capabilities keep changing, and mitigations are being rolled out at a similar pace.

By letting GenAI reason on behalf of our users with their identities, we've opened up a new attack vector where adversaries can target our AI systems instead of our users for similar results. They do it with [Promptware](https://labs.zenity.io/p/rce#promptware-the-missing-piece-and-a-), content with malicious instructions. Promptware doesn't usually execute code, instead it executes tools and composes them into programs with natural language for an equal effect.

Our first collective attempt at fighting malware was Antivirus software which tried to enumerate every known malware out there. We've taken the same approach with promptware, trying to fix the problem by enumerating bad prompts. This does not work, nor is prompt injection a problem [we can simply fix](https://simonwillison.net/2022/Sep/17/prompt-injection-more-ai/). Instead, its a problem we can to manage. Learning from EDRs, we need to adopt a defense-in-depth approach that is focused on malicious behavior rather than malicious static content. The goal of this project is to document and share knowledge of those behaviors and to look beyond prompt injection at the entire lifecycle of a promptware attack.

This project was inspired by the awesome work of others who successfully applied the attacks approach to [M365](https://medium.com/@johnlatwc/the-githubification-of-infosec-afbdbfaad1d1),[containers](https://www.microsoft.com/en-us/security/blog/2021/07/21/the-evolution-of-a-matrix-how-attck-for-containers-was-built/) and [SaaS](https://github.com/pushsecurity/saas-attacks).


## How To Contribute Content?

| :point_up:    | You can edit any `.json` file or create a new one directly in your browser to easily contribute! |
|------|:---|

Improve our knowledge base by editing or adding files within these directories:

```
|
--| tactic
--| technique
--| procedure
--| entity
--| platform
```

File schema and how things work:
* Your change will be automatically tested for compliance with the [schema](/schema/) once a PR is created.
* Once a PR gets merged to `main`, the website will automatically update within a few minutes.
* You can check out the [schema](/schema/) directory or look at other files for example, you'll find them at:

## More Information

Check out additional resources and docs:

- [Developer Docs](contribute.md)
- [Q&A][qna.md]
