const steps = [
  { title: "Legg inn begge dokumentene", text: "Lim inn teksten eller last opp PDF av tilbudet og kontrakten." },
  { title: "Se hva som er endret", text: "Hvert funn viser sitat fra dokumentene, så du kan sjekke det selv." },
  { title: "Send svaret", text: "Velg punktene du vil ta opp, og kopier et svarutkast til kunden." },
];

const terms = [
  { name: "Leveranse", text: "Hva som skal leveres, og når." },
  { name: "Betaling", text: "Pris og betalingsfrist." },
  { name: "Ekstraarbeid", text: "Revisjonsrunder og arbeid utenfor avtalen." },
  { name: "Ansvar", text: "Ansvarsbegrensning og hvem som bærer risikoen." },
];

export function Landing({ toolHref }: { toolHref: string }) {
  return (
    <main>
      <div className="hero">
        <div className="wrap">
          <nav className="hero-nav" aria-label="Hovedmeny">
            <a className="brand" href="#/">Kontraktsstøtte</a>
            <a className="hero-nav-link" href="#slik-fungerer-det">Slik fungerer det</a>
          </nav>
          <h1 className="hero-title" tabIndex={-1}>Sier kontrakten det samme som tilbudet ditt?</h1>
          <div className="hero-intro">
            <p>
              Lim inn eller last opp tilbudet og kundens kontrakt. Du ser hva som er endret, med sitat fra dokumentene,
              og får et svarutkast du kan sende til kunden.
            </p>
            <a className="button" href={toolHref}>Sjekk kontrakten</a>
          </div>
        </div>
      </div>

      <figure className="example wrap">
        <div className="columns">
          <div className="example-sheet">
            <p className="example-source">Tilbud</p>
            <p className="example-text">
              Design av én landingsside med to revisjonsrunder. Betaling innen <mark>14 dager</mark> etter faktura.
            </p>
          </div>
          <div className="example-sheet">
            <p className="example-source">Kundens kontrakt</p>
            <p className="example-text">
              Design av én landingsside med to revisjonsrunder. Betaling innen{" "}
              <mark className="example-changed">60 dager</mark> etter faktura.
            </p>
          </div>
        </div>
        <div className="example-finding">
          <span className="example-status">Avvik</span>
          <span>Kontrakten gir kunden 46 dager lengre betalingsfrist enn tilbudet.</span>
        </div>
        <figcaption className="example-caption">Fiktivt eksempel</figcaption>
      </figure>

      <section className="landing-section wrap" id="slik-fungerer-det" aria-labelledby="steps-title">
        <h2 className="landing-heading" id="steps-title">Slik fungerer det</h2>
        <ol className="steps">
          {steps.map((step) => (
            <li key={step.title}>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing-section terms wrap" aria-labelledby="terms-title">
        <div>
          <h2 className="landing-heading" id="terms-title">Dette går vi gjennom</h2>
          <p className="terms-lead">
            Vi ser etter forskjeller i innhold, ikke i ordlyd. 14 dager og to uker er det samme.
          </p>
        </div>
        <dl className="terms-list">
          {terms.map((term) => (
            <div key={term.name}>
              <dt>{term.name}</dt>
              <dd>{term.text}</dd>
            </div>
          ))}
        </dl>
      </section>

      <div className="wrap">
        <section className="closing" aria-labelledby="closing-title">
          <h2 id="closing-title">Har du fått en kontrakt du skal signere?</h2>
          <a className="button button-pad" href={toolHref}>Sjekk kontrakten</a>
        </section>
      </div>
    </main>
  );
}
