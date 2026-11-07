# GDPR Privacy Notice — Draft Template

> **LEGAL REVIEW REQUIRED — THIS IS NOT LEGAL ADVICE.**
> This is a draft template for a GDPR privacy notice. It must be reviewed by qualified EU/EEA
> data protection counsel and adapted to the actual processing activities and legal entity
> before publication. It does not assert that a Data Protection Officer has been appointed,
> that an EU representative has been designated, or that Topiome holds any certification.

| Field | Value |
|---|---|
| Version | 0.1 — draft |
| Last updated | 6 November 2026 |
| Effective date | [EFFECTIVE DATE] |
| Controller | [COMPANY LEGAL NAME] |
| Applies to | Visitors, account users, organization administrators, billing and support contacts in the EU/EEA |
| Product scope | Topiome multi-tenant SaaS for spatial transcriptomics — research use only |

**Türkçe belgeler / Turkish index:** [README](./README.md) · [KVKK Aydınlatma Metni](./kvkk-aydinlatma.md) · [DPA](./dpa.md) · [Saklama Politikası](./retention-policy.md) · [Alt İşleyiciler](./subprocessors.md) · [Veri Sınıflandırması](./data-classification.md)

## 1. Who we are and our roles

Topiome is a research software platform operated by **[COMPANY LEGAL NAME]** ("Topiome", "we",
"us"), with its registered address at **[ADDRESS]**. For privacy questions, contact
**[PRIVACY EMAIL]**. Our Data Protection Officer is **[DATA PROTECTION OFFICER NAME/ROLE]**
(if appointed; otherwise state "not appointed"). Our EU representative under Article 27 GDPR is
**[EU REPRESENTATIVE NAME, ADDRESS, EMAIL]** (if required; otherwise state why not).

We act in two different roles:

| Data | Controller | Topiome's role | Governing document |
|---|---|---|---|
| Account, contact, organization membership, authentication, usage/audit, billing and support data | [COMPANY LEGAL NAME] | **Controller** | This notice |
| Research data uploaded by a customer (sample files, `sample.json` metadata, analysis parameters, derived outputs, reports) | The customer institution | **Processor** | [DPA](./dpa.md) and the customer's own notice |
| Subprocessor services | Customer (for research data) / Topiome (for its own data) | Part of the processing chain | [DPA](./dpa.md) and [Subprocessors](./subprocessors.md) |

> **Research data:** The customer institution is the controller of research data it uploads.
> Topiome processes that data only on the customer's documented instructions under the DPA. The
> customer is responsible for its own transparency notice, ethics approval, consent, and any
> required legal basis for its research data. Topiome does not use customer research data to
> train shared models without a separate written agreement.

## 2. Scope of this notice

This notice explains how we process personal data when you:

- visit our website or request a demo;
- create or use a Topiome account, or are invited to an organization;
- administer an organization, manage billing, or contact support;
- communicate with us about the service, security, or legal matters.

It does not govern research data uploaded by a customer institution, for which the institution
is the controller. If you are a research participant or a person whose data appears in a
customer's research files, please contact the institution that uploaded the data. If we receive
your request, we will forward it to the relevant customer unless the law requires otherwise.

## 3. Personal data we collect

| Category | Examples | Source | Required? |
|---|---|---|---|
| **Identity and contact** | Name, email, phone (optional), institution, job title, country | You, your organization | Name and email are required to create an account |
| **Account and organization** | Username, password hash, role (owner/admin/analyst/viewer), organization name, invitations, language and notification preferences | You, organization admin | Required |
| **Authentication and session** | Session cookie, session age, IP address, browser/device information, failed login records, MFA status (if enabled) | Technical systems | Required for security |
| **Usage and audit** | Pages/actions, run start/finish, upload/download/delete, report generation/sharing, API key actions, error records | Technical systems | Required to provide and secure the service |
| **Billing** | Plan, invoices, payment status, tax information, Stripe customer/transaction reference; **card data is handled by Stripe and not stored by Topiome** | You, payment provider | Required for contract and tax duties |
| **Support** | Request content, attachments, correspondence, resolution notes | You | If you contact support |
| **Marketing preferences** | Email consent, opens/clicks (if enabled), event registration, cookie choices | You, technical systems | Optional; consent-based where required |
| **Security and incidents** | Access logs, incident assessment notes, legal hold records | Technical systems, legal/compliance | Required for security and legal obligations |

We do not intentionally collect special category data through account registration. Customer
research data must be de-identified and must not contain identifiable patient data in Phase 1.
See section 5.

## 4. Purposes and lawful bases

Under Article 6(1) GDPR, we rely on the following bases. Where we rely on legitimate interests,
we carry out and document a balancing test. Where consent is required, you may withdraw it at
any time without affecting processing that occurred before withdrawal.

| Purpose | Lawful basis | Notes |
|---|---|---|
| Create and manage accounts; provide the service; run analyses; store results; generate reports | Art. 6(1)(b) — contract | Necessary to perform the contract with you or your organization |
| Organization and role administration; collaboration features | Art. 6(1)(b) — contract | Includes owner/admin/analyst/viewer permissions |
| Authentication, security, fraud/abuse prevention, audit logging | Art. 6(1)(f) — legitimate interests | Interest in protecting the service, customers, and data; balancing test required |
| Billing, invoicing, tax and accounting | Art. 6(1)(b) — contract; Art. 6(1)(c) — legal obligation | Card data handled by the payment provider |
| Support and troubleshooting | Art. 6(1)(b) — contract; Art. 6(1)(f) — legitimate interests | Scope depends on the request |
| Legal claims, regulatory requests, breach notifications, retention | Art. 6(1)(c) — legal obligation; Art. 6(1)(f) — legitimate interests | Requests are assessed for legal validity |
| Aggregated, de-identified product analytics | Art. 6(1)(f) — legitimate interests | We use aggregated data where possible; no re-identification |
| Marketing emails and event invitations | Art. 6(1)(a) — consent; or Art. 6(1)(f) where permitted | Opt-out available; ePrivacy rules apply |
| Optional cookies and analytics | Art. 6(1)(a) — consent | Strictly necessary cookies do not require consent |
| Special category data (exceptional research upload) | Art. 9(2)(a) — explicit consent, or Art. 9(2)(j) — research with legal safeguards | Only with a separate agreement and applicable Member State law; otherwise prohibited |

We do not make automated decisions about individuals that produce legal or similarly
significant effects. Analysis outputs are computational research inferences about samples, not
decisions about individuals. We do not sell personal data.

## 5. Research data: de-identification, ethics, and customer responsibility

Topiome is **for research use only (RUO)**. It is not a medical device and is not intended for
diagnosis, prognosis, treatment selection, therapy monitoring, or clinical decision-making.

- Customers must upload **de-identified** research data. Identifiable patient data (name,
  medical record number, date of birth, full address, facial images, identifiers in free text)
  is not accepted in Phase 1.
- Customers are responsible for obtaining **ethics committee approval**, participant consent
  or another lawful basis, data-use permissions, and any institutional approvals required for
  their research.
- De-identification is not automatically anonymization. Genetic data, small cohorts, rare
  diseases, and combined metadata can make re-identification possible. The customer must assess
  residual risk and must not attempt re-identification.
- Special category data (health, genetic, biometric, racial/ethnic origin, political opinions,
  religion, sexual life, criminal convictions) requires a separate written agreement, explicit
  consent or another Article 9 basis, a DPIA where required, and additional safeguards. Research
  purpose alone is not automatically sufficient.
- We do not use customer research data for shared model training, advertising, or sale without
  a separate written agreement.
- Reports and shared outputs must retain the RUO notice.

## 6. International transfers

Topiome is designed for customers in the EU/EEA, the US, and Türkiye. Our default hosting region
is planned as **[REGION — e.g., EU / Frankfurt]**, with an optional Türkiye region
**[STATUS]**. Data may be processed by subprocessors in the EU/EEA, the US, the UK, or Türkiye.

Where we transfer personal data outside the EU/EEA to a country without an adequacy decision,
we rely on appropriate safeguards, typically the **Standard Contractual Clauses (EU) 2021/914**
(Module 2: controller to processor, or Module 3 where applicable), together with supplementary
measures informed by a transfer impact assessment (TIA). Where a provider is certified under an
applicable adequacy framework, we may rely on that framework after verifying its current scope.
We do not rely on an adequacy mechanism without confirming that it covers the relevant entity
and processing.

For transfers from Türkiye, we use the mechanisms available under KVKK Article 9, including an
adequacy decision, the KVKK standard contract, or another permitted ground. Transfers are
documented in our processing register and in the DPA.

You can request more information about the safeguard used for a specific transfer by contacting
**[PRIVACY EMAIL]**.

## 7. How long we keep personal data

We keep personal data only as long as necessary for the purposes described in this notice,
unless a longer period is required by law or a legal hold. The detailed schedule is in our
[Retention Policy](./retention-policy.md). In summary:

| Data | Default retention |
|---|---|
| Account and organization data | While the account is active + 12 months after closure |
| Session data | 7 days (session lifetime); failed login records 90 days |
| Customer research data (raw, derived, reports) | 24 months after last activity (organization-configurable) |
| Audit logs | 24 months (extendable for enterprise customers) |
| Application/access logs | 90 days hot, 1 year archive |
| Backups | 30-day rolling cycle |
| Billing and tax records | 10 years, subject to applicable law and accountant confirmation |
| Support tickets | 24 months after closure |
| Marketing preferences | Until withdrawal + 24 months |

When the retention period ends, data is deleted, destroyed, or anonymized. Deletion may be
suspended for a legal hold, an ongoing dispute, or a mandatory retention duty; the reason is
documented. Customer research data is deleted according to the DPA and the customer's settings.

## 8. Security

We use technical and organizational measures appropriate to the risk, including:

- TLS 1.2+ in transit; HSTS and secure cookie settings;
- provider-level disk encryption at rest; application-level encryption for sensitive fields
  (Phase 2);
- Argon2id password hashing; session expiry and revocation;
- organization-level tenant isolation and role-based access control (owner/admin/analyst/viewer);
- signed URLs limited to 15 minutes for downloads and 60 minutes for uploads; no public buckets;
- audit logging of authentication, role changes, uploads/downloads/deletions, runs, reports, API
  keys, and billing changes; file contents are not logged;
- encrypted backups in a separate account/region with a 30-day cycle;
- dependency scanning, secure development practices, access reviews, and an incident response
  plan;
- MFA (TOTP) is on the roadmap and is not guaranteed as of the effective date of this template.

No system is perfectly secure. If you suspect a security issue, contact **[SECURITY EMAIL]**.
This notice does not claim ISO 27001, SOC 2, HIPAA, or any other certification. Current controls
are documented in [../SECURITY.md](../SECURITY.md).

## 9. Your rights

Subject to applicable law, you have the right to:

1. **Access** your personal data and receive a copy (Art. 15).
2. **Rectify** inaccurate or incomplete data (Art. 16).
3. **Erase** data where the conditions are met (Art. 17).
4. **Restrict** processing where the conditions are met (Art. 18).
5. **Data portability** for data you provided, where processing is based on contract or consent
   and carried out by automated means (Art. 20).
6. **Object** to processing based on legitimate interests, and to direct marketing at any time
   (Art. 21).
7. **Withdraw consent** at any time where processing is based on consent (Art. 7(3)).
8. **Lodge a complaint** with your local supervisory authority (Art. 77).

To exercise your rights, email **[PRIVACY EMAIL]** or write to **[ADDRESS]**. We may ask for
information to verify your identity. We respond within one month; the period may be extended by
up to two further months for complex requests, and we will explain the extension. Requests are
generally free of charge; we may charge a reasonable fee or refuse manifestly unfounded or
excessive requests as permitted by law. Please do not send identifiable patient data or research
files with your request.

If your request concerns research data uploaded by a customer institution, the institution is
the controller. We will forward your request to it and assist as required by the DPA, unless the
law requires us to act directly.

## 10. Cookies and similar technologies

We use strictly necessary cookies for authentication, security, and load balancing. These do not
require consent. Optional analytics or marketing cookies, if introduced, will be set only with
your consent where required, and you will be able to withdraw or change your choices. We do not
use non-essential tracking cookies by default. Cookie details are maintained in our cookie
notice at **[COOKIE NOTICE URL]**.

## 11. Children

Topiome is intended for institutional research users and is not directed to children under 18.
We do not knowingly create accounts for children. Research data may include de-identified data
relating to children; the customer institution is responsible for ethics approval, consent, and
applicable safeguards.

## 12. Changes to this notice

We may update this notice to reflect changes in the service, subprocessors, or law. Material
changes will be posted on this page and notified to organization owners by email before they
take effect where required. The effective date and version are shown at the top. Previous
versions are available at **[VERSION ARCHIVE URL]**.

## 13. Contact

| Matter | Contact |
|---|---|
| Privacy and data subject requests | **[PRIVACY EMAIL]** |
| Data Protection Officer | **[DATA PROTECTION OFFICER NAME/ROLE]** — if appointed; otherwise "not appointed" |
| EU representative (Art. 27) | **[EU REPRESENTATIVE NAME, ADDRESS, EMAIL]** — if required |
| Postal address | **[ADDRESS]** |
| Security incidents | **[SECURITY EMAIL]** |
| Legal | **[LEGAL EMAIL]** |

## 14. Turkish-language documents

The following Turkish-language templates form the local index and should be read together with
this notice:

- [Hukuki ve Uyum Belgeleri — README](./README.md)
- [KVKK Aydınlatma Metni](./kvkk-aydinlatma.md)
- [Veri İşleme Sözleşmesi (DPA)](./dpa.md)
- [Saklama Politikası](./retention-policy.md)
- [Alt İşleyiciler](./subprocessors.md)
- [Veri Sınıflandırması](./data-classification.md)

> **Note:** This English notice is a template. It does not create a legal entity, appoint a DPO
> or EU representative, or certify compliance with the GDPR or any other framework. It must be
> localized and reviewed before publication.
