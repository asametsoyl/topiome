import { LegalPage, LegalSection } from "@/components/marketing/legal-page";

export const metadata = { title: "Privacy policy" };

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Privacy policy"
      updated="November 6, 2026"
      draft
      intro="This draft describes how Topiome handles account data and research data. It is not legal advice and will be reviewed by counsel before commercial launch."
    >
      <LegalSection title="1. Who we are">
        <p>
          Topiome is a research software platform. For account data, Topiome acts as the data
          controller. For research data uploaded by a laboratory, the laboratory (or its
          institution) is the controller and Topiome acts as a processor under a data processing
          agreement.
        </p>
      </LegalSection>

      <LegalSection title="2. What we collect">
        <ul className="list-disc space-y-2 pl-5">
          <li>Account data: name, email, organization, role, authentication metadata.</li>
          <li>Research data: files you upload, sample metadata, analysis parameters and results.</li>
          <li>Usage data: pages viewed, actions taken, run status, IP address, user agent.</li>
          <li>Billing data: plan, invoices, and payment status (card data is handled by Stripe).</li>
        </ul>
        <p>
          Do not upload identifiable patient data unless a separate agreement and appropriate
          safeguards are in place. Phase 1 is designed for de-identified or synthetic research
          data.
        </p>
      </LegalSection>

      <LegalSection title="3. How we use data">
        <ul className="list-disc space-y-2 pl-5">
          <li>Provide the service: run analyses, store results, generate reports.</li>
          <li>Secure the service: authentication, audit logs, abuse prevention.</li>
          <li>Support you: respond to requests and troubleshoot runs.</li>
          <li>Improve the product: aggregated, de-identified usage metrics.</li>
        </ul>
        <p>
          We do not use your research data to train shared models without explicit written
          agreement. We do not sell personal data.
        </p>
      </LegalSection>

      <LegalSection title="4. Storage and retention">
        <p>
          Data is stored in the region selected for your workspace. Default retention for
          project data is 24 months after the last activity, unless your organization sets a
          different policy. Deletion requests are processed within 30 days, including backups
          where technically feasible.
        </p>
      </LegalSection>

      <LegalSection title="5. Sub-processors">
        <p>
          We use infrastructure, storage, payment, and email providers. A current list is
          available on request. Sub-processors are bound by data protection terms and, where
          required, standard contractual clauses.
        </p>
      </LegalSection>

      <LegalSection title="6. Your rights">
        <p>
          Depending on your jurisdiction (KVKK, GDPR, or similar), you may request access,
          correction, deletion, portability, or restriction of your personal data. Contact{" "}
          <a href="mailto:privacy@topiome.com" className="text-acid underline decoration-acid/30 underline-offset-2">
            privacy@topiome.com
          </a>
          . We respond within 30 days.
        </p>
      </LegalSection>

      <LegalSection title="7. Security">
        <p>
          We use encryption in transit, organization-level isolation, hashed credentials,
          role-based access, audit logging, and least-privilege infrastructure. No system is
          perfectly secure; report suspected issues to{" "}
          <a href="mailto:security@topiome.com" className="text-acid underline decoration-acid/30 underline-offset-2">
            security@topiome.com
          </a>
          .
        </p>
      </LegalSection>

      <LegalSection title="8. Changes">
        <p>
          We will post material changes on this page and notify workspace owners by email.
          Continued use after the effective date constitutes acceptance.
        </p>
      </LegalSection>
    </LegalPage>
  );
}
