import { LegalPage, LegalSection } from "@/components/marketing/legal-page";
import { RuoNotice } from "@/components/ui/ruo-notice";

export const metadata = { title: "Research Use Only policy" };

export default function RuoPolicyPage() {
  return (
    <LegalPage
      title="Research Use Only policy"
      updated="November 7, 2026"
      intro="Topiome is developing computational research methods for predicting cellular responses to defined perturbations. The current research direction has not produced a validated prediction model."
    >
      <RuoNotice />

      <LegalSection title="1. Intended use">
        <p>
          Topiome's research direction is exploratory computational biology: evaluating whether models can predict measured cellular responses to genetic perturbations in defined experimental contexts.
        </p>
        <p>
          Topiome is not intended for diagnosis, prognosis, treatment selection, patient management, or clinical decision-making. No output is a therapeutic recommendation or evidence that an intervention will work in a person.
        </p>
      </LegalSection>

      <LegalSection title="2. What computational predictions mean">
        <p>
          A predicted response is a model estimate conditioned on its training data, perturbation, assay, time point, dose, and cell context. Public-data benchmark performance does not by itself demonstrate causal mechanism, transfer to a new biological system, or experimental utility.
        </p>
        <p>
          Prospective biological claims require independently generated experimental measurements. Until such validation exists, outputs must be treated as research hypotheses and not as established biology.
        </p>
      </LegalSection>

      <LegalSection title="3. Validation status">
        <p>
          Topiome has not yet trained or validated a perturbation-response prediction model. Research code, benchmark results, and future prototypes will be labeled with their evidence status and limitations. A held-out computational benchmark is not independent experimental validation.
        </p>
      </LegalSection>

      <LegalSection title="4. User responsibilities">
        <ul className="list-disc space-y-2 pl-5">
          <li>Use only data you are authorized to access and process.</li>
          <li>Check the license and terms for each public dataset before reuse.</li>
          <li>Do not use research outputs to make clinical or patient-level decisions.</li>
          <li>Independently test any biological hypothesis before relying on it.</li>
          <li>Retain the RUO notice when sharing Topiome research outputs.</li>
        </ul>
      </LegalSection>

      <LegalSection title="5. Contact">
        <p>
          Questions about intended use or research collaboration: {" "}
          <a href="mailto:hello@topiome.com" className="text-acid underline decoration-acid/30 underline-offset-2">hello@topiome.com</a>.
        </p>
      </LegalSection>
    </LegalPage>
  );
}
