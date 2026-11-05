import { LegalPage, LegalSection } from "@/components/marketing/legal-page";
import { RuoNotice } from "@/components/ui/ruo-notice";

export const metadata = { title: "Research Use Only policy" };

export default function RuoPolicyPage() {
  return (
    <LegalPage
      title="Research Use Only policy"
      updated="November 6, 2026"
      intro="Topiome is a research tool. This policy defines the boundary between research use and clinical use, and the language we use to describe results."
    >
      <RuoNotice />

      <LegalSection title="1. Intended use">
        <p>
          Topiome is intended for research use by scientists, bioinformaticians, and research
          laboratories. It supports exploration of spatial transcriptomics data: cell-type
          composition, spatial domain structure, target gene expression, and uncertainty.
        </p>
        <p>
          Topiome is <strong className="text-bone">not</strong> intended for diagnosis,
          prognosis, treatment selection, therapy monitoring, or clinical decision-making. It is
          not a medical device and has not been cleared or approved by the FDA, EMA, TİTCK, or
          any other regulator.
        </p>
      </LegalSection>

      <LegalSection title="2. What results mean">
        <p>
          Results are computational inferences from research data. Deconvolution estimates
          composition from bulk spot expression; spatial domains are computational regions
          labeled by marker scores; target scores are research prioritization signals, not
          therapeutic recommendations.
        </p>
        <p>
          Every result depends on data quality, reference atlas coverage, parameters, and the
          validity of the disease pack. Results must be independently validated before being
          used in any research decision, publication, or downstream study.
        </p>
      </LegalSection>

      <LegalSection title="3. No clinical claims">
        <p>
          You may not represent Topiome output as a diagnosis, a clinical finding, a treatment
          recommendation, or a substitute for pathologist review. Marketing, publications, and
          internal communications must retain the RUO qualifier and must not imply clinical
          validation unless a separate written agreement and regulatory pathway exist.
        </p>
      </LegalSection>

      <LegalSection title="4. Validation status">
        <p>
          Disease packs carry a status: <span className="font-mono text-teal">draft</span>,{" "}
          <span className="font-mono text-teal">beta</span>,{" "}
          <span className="font-mono text-teal">validated</span>, or{" "}
          <span className="font-mono text-teal">deprecated</span>. Beta means the baseline runs
          but validation is incomplete. Draft means the pack is under development. No pack is
          clinically validated.
        </p>
        <p>
          Synthetic benchmarks test numerical recovery against known ground truth. They do not
          prove biological generalization or clinical utility.
        </p>
      </LegalSection>

      <LegalSection title="5. User responsibilities">
        <ul className="list-disc space-y-2 pl-5">
          <li>Confirm that you have the right to use the data you upload.</li>
          <li>Obtain ethics approval and consent where required by your institution.</li>
          <li>Do not upload identifiable patient data without an appropriate agreement.</li>
          <li>Retain the RUO notice in shared reports and publications.</li>
          <li>Independently validate any result before relying on it.</li>
        </ul>
      </LegalSection>

      <LegalSection title="6. Contact">
        <p>
          Questions about intended use or clinical partnerships:{" "}
          <a href="mailto:hello@topiome.com" className="text-acid underline decoration-acid/30 underline-offset-2">
            hello@topiome.com
          </a>
          .
        </p>
      </LegalSection>
    </LegalPage>
  );
}
