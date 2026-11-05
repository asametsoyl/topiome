import { LegalPage, LegalSection } from "@/components/marketing/legal-page";

export const metadata = { title: "Terms of service" };

export default function TermsPage() {
  return (
    <LegalPage
      title="Terms of service"
      updated="November 6, 2026"
      draft
      intro="These draft terms govern access to Topiome. They are not legal advice and will be reviewed by counsel before commercial launch."
    >
      <LegalSection title="1. Agreement">
        <p>
          By creating an account or using Topiome, you agree to these terms on behalf of
          yourself and the organization you represent. If you do not have authority to bind the
          organization, do not use the service.
        </p>
      </LegalSection>

      <LegalSection title="2. Research use only">
        <p>
          Topiome is provided for research use only. It is not a medical device and must not be
          used for diagnosis, prognosis, treatment selection, or clinical decision-making. You
          are responsible for retaining the RUO notice in shared outputs.
        </p>
      </LegalSection>

      <LegalSection title="3. Accounts and security">
        <p>
          You are responsible for safeguarding credentials and for activity under your account.
          Notify us immediately of suspected unauthorized access. We may suspend accounts that
          threaten the service or violate these terms.
        </p>
      </LegalSection>

      <LegalSection title="4. Your data">
        <p>
          You retain ownership of the data you upload. You grant Topiome a limited license to
          process that data to provide the service. You confirm that you have the rights and
          ethics approvals required to upload it. We do not use research data to train shared
          models without explicit written agreement.
        </p>
      </LegalSection>

      <LegalSection title="5. Acceptable use">
        <ul className="list-disc space-y-2 pl-5">
          <li>Do not upload malware, unlawful content, or data you do not have rights to use.</li>
          <li>Do not attempt to access another organization&apos;s data or bypass access controls.</li>
          <li>Do not reverse engineer, resell, or benchmark the service for a competing product.</li>
          <li>Do not represent Topiome output as clinical advice or a validated diagnostic.</li>
        </ul>
      </LegalSection>

      <LegalSection title="6. Service availability">
        <p>
          We aim for high availability but do not guarantee uninterrupted service. Maintenance,
          upgrades, and third-party outages may affect access. Analysis runs are asynchronous;
          you are responsible for reviewing status and results.
        </p>
      </LegalSection>

      <LegalSection title="7. Intellectual property">
        <p>
          Topiome software, disease packs, documentation, and brand are owned by Topiome or its
          licensors. You receive a non-exclusive, non-transferable right to use the service
          during your subscription. Feedback may be used to improve the product without
          obligation.
        </p>
      </LegalSection>

      <LegalSection title="8. Disclaimers">
        <p>
          The service is provided &quot;as is&quot; and &quot;as available.&quot; To the maximum
          extent permitted by law, Topiome disclaims warranties of merchantability, fitness for
          a particular purpose, and non-infringement. Results are computational inferences and
          must be independently validated.
        </p>
      </LegalSection>

      <LegalSection title="9. Limitation of liability">
        <p>
          To the maximum extent permitted by law, Topiome is not liable for indirect,
          incidental, special, consequential, or punitive damages, or for lost data, profits, or
          research opportunities. Aggregate liability is limited to the fees paid in the twelve
          months preceding the claim.
        </p>
      </LegalSection>

      <LegalSection title="10. Termination">
        <p>
          You may stop using the service at any time. We may terminate or suspend access for
          material breach, non-payment, or risk to the service. On termination, you may export
          your results during the stated retention window; afterward, data may be deleted.
        </p>
      </LegalSection>

      <LegalSection title="11. Contact">
        <p>
          Legal inquiries:{" "}
          <a href="mailto:legal@topiome.com" className="text-acid underline decoration-acid/30 underline-offset-2">
            legal@topiome.com
          </a>
          .
        </p>
      </LegalSection>
    </LegalPage>
  );
}
