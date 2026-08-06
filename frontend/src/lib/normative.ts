export type CategoriaNormativa = {
  slug: string;
  nome: string;
  argomenti: string[];
};

export const CATEGORIE_NORMATIVE: CategoriaNormativa[] = [
  {
    slug: "amministrazione",
    nome: "Amministrazione",
    argomenti: [
      "Cfi - Cfg",
      "Bilinguismo",
      "Concertazione economica e normativa decreti ministeriali",
      "Cud - Dichiarazione Redditi",
      "Danno erariale",
      "FESI",
      "Finanziamenti",
      "Trattamento economico",
      "Varie",
      "Servizio isolato",
    ],
  },
  {
    slug: "benessere",
    nome: "Benessere",
    argomenti: [
      "Alloggi",
      "Trasporti pubblici",
      "Asili nido",
      "Convenzioni",
      "Foresterie e alloggi",
      "Interventi assistenziali",
    ],
  },
  {
    slug: "diritti-e-tutele",
    nome: "Diritti e Tutele",
    argomenti: [
      "Attività elettorale per i militari",
      "Assemblee e visite",
      "Deleghe sindacali",
      "Costituzione associazioni sindacali",
      "Distacchi e permessi",
      "Diritto allo studio",
      "Legge 104/92",
      "Circolari e Direttive sindacali",
      "Licenze e permessi",
      "Sicurezza sul lavoro",
      "Tutela della famiglia, maternità, paternità",
    ],
  },
  {
    slug: "logistico",
    nome: "Logistico",
    argomenti: [
      "Capomacchina e Conduttore",
      "Tramat",
      "Automezzi",
      "Commissariato",
      "Patenti e corsi",
      "Sanità",
      "Vettovagliamento",
    ],
  },
  {
    slug: "operazioni",
    nome: "Operazioni",
    argomenti: ["Addestramento", "Strade sicure"],
  },
  {
    slug: "pensioni",
    nome: "Pensioni",
    argomenti: ["Ausiliaria", "TFS/TFR", "Altro"],
  },
  {
    slug: "personale",
    nome: "Personale",
    argomenti: [
      "Sottufficiali",
      "Cause di servizio - cure - varie",
      "Vittime del dovere e terrorismo - Veterano",
      "VFT - VFP1 - VFP",
      "Onorificenze, medaglie, riconoscimenti, brevetti",
      "Graduati",
      "Attività extraprofessionale",
      "Avanzamenti - Documentazione caratteristica e matricola",
      "Cura decoro uniformi",
      "Ufficiali",
      "Disciplina",
      "Benefici combattentistici",
      "Impiego del personale",
      "Incarichi",
      "Orario di lavoro",
      "PEFO",
      "Trasferimenti",
    ],
  },
];
