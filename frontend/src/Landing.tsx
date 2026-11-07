import { useState } from "react";

type Mark = "endret" | "mangler" | "taktikk" | "press";

const wallText: [string, Mark?][] = [
  ["Oppdragsgiver betaler innen "], ["60 dager", "endret"], [" etter mottatt faktura. Leverandøren skal levere avtalt omfang innen fristen. "],
  ["Ingen ansvarsbegrensning", "mangler"], [" er avtalt for oppdraget. Revisjoner utføres "], ["til kunden er fornøyd", "endret"],
  [". Avtalen er underlagt norsk rett. Vi forventer at leverandøren "], ["aksepterer vilkårene", "taktikk"], [" uten endringer. "],
  ["Ingen betaling ved avbrutt oppdrag", "mangler"], [" er omtalt. Ekstraarbeid er "], ["inkludert i fastprisen", "endret"],
  [". Tilbudet gjelder bare "], ["frem til fredag", "press"], [". Alle rettigheter overføres "], ["ved signering", "endret"], [". "],
  ["Ingen rett til å vise arbeidet", "mangler"], [" i portefølje er avtalt. "], ["Dette er våre standardvilkår", "taktikk"],
  [" for alle leverandører. Vi har "], ["flere aktuelle leverandører", "press"], [". Endringer avtales mellom partene. "],
];

const wallRepeats = Array.from({ length: 10 }, (_, index) => index);

const questions = [
  "Hva er endret?",
  "Hva mangler?",
  "Hva bør du kreve?",
  "Hvordan sier du det?",
  "Hva kan du gi for å få noe tilbake?",
];

const tickerRepeats = [0, 1, 2, 3];

const advice = [
  {
    tab: "Avvik",
    title: "Tilbudet sa 14 dager.",
    text: "Kontrakten gir kunden 46 dager lengre tid. Du finansierer oppdraget i over en måned ekstra.",
  },
  {
    tab: "Krav",
    title: "Be om en klar forfallsdato og forsinkelsesrente.",
    text: "Hvis lang frist er uunngåelig, kan du be om delbetaling underveis.",
  },
  {
    tab: "Språk",
    title: "«Vi leverer gjerne på 60 dager hvis prisen justeres. Ellers holder vi oss til 14.»",
    text: "Du sier ikke nei. Du gir kunden to valg, og begge fungerer for deg.",
  },
  {
    tab: "Psykologi",
    title: "Gi noe for å få noe.",
    text: "Start med det dere er enige om. Tilby noe som koster deg lite, for eksempel en ekstra statusrunde, mot kortere frist.",
  },
];

export function Landing({ toolHref }: { toolHref: string }) {
  const [active, setActive] = useState(0);

  return (
    <main>
      <div className="hero navy">
        <div className="wall" aria-hidden="true">
          {wallRepeats.map((repeat) =>
            wallText.map(([text, mark], index) =>
              mark ? <b key={`${repeat}-${index}`} className={`wall-${mark}`}>{text}</b> : text,
            ),
          )}
        </div>
        <div className="hero-content wrap">
          <h1 className="hero-title" tabIndex={-1}>Ikke bare signer. <span>Forhandle.</span></h1>
          <p className="hero-lead">Få hjelp til å se hva som er endret, hva du bør kreve og hvordan du får kunden med på det.</p>
          <a className="button button-large" href={toolHref}>Sjekk kontrakten</a>
        </div>
      </div>

      <div className="ticker" aria-hidden="true">
        <div className="ticker-track">
          {tickerRepeats.map((repeat) => questions.map((question) => <span key={`${repeat}-${question}`}>{question}</span>))}
        </div>
      </div>

      <section className="demo wrap" id="eksempel" aria-labelledby="demo-title">
        <h2 className="big-heading" id="demo-title">Én setning. Fire typer råd.</h2>
        <p className="demo-clause">«Betaling innen <mark>60 dager</mark> etter faktura.»</p>
        <div className="tabs" role="tablist" aria-label="Typer råd">
          {advice.map((item, index) => (
            <button
              key={item.tab}
              type="button"
              role="tab"
              aria-selected={index === active}
              aria-controls="advice-panel"
              onClick={() => setActive(index)}
            >
              {item.tab}
            </button>
          ))}
        </div>
        <div className="demo-panel" id="advice-panel" role="tabpanel" aria-live="polite">
          <div key={active} className="demo-panel-content">
            <p className="demo-panel-title">{advice[active].title}</p>
            <p>{advice[active].text}</p>
          </div>
        </div>
        <p className="demo-caption">Fiktivt eksempel</p>
      </section>

      <section className="closing navy" aria-labelledby="closing-title">
        <div className="wrap">
          <h2 className="big-heading" id="closing-title">Hva ville du endret hvis du visste at du kunne?</h2>
          <a className="button button-large" href={toolHref}>Sjekk kontrakten</a>
        </div>
      </section>
    </main>
  );
}
