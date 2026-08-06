import calabreseFoto from "@/assets/organizzazione/calabrese.jpg";
import leoneFoto from "@/assets/organizzazione/leone.jpg";
import moscatelliFoto from "@/assets/organizzazione/moscatelli.jpg";

export const PRESIDENTE = {
  ruolo: "Presidente",
  cognome: "Calabrese",
  email: "presidentelombardia@siamoesercito.org",
  foto: calabreseFoto,
};

export const SEGRETARIO = {
  ruolo: "Segretario",
  cognome: "Leone",
  email: "segretariolombardia@siamoesercito.org",
  foto: leoneFoto,
};

export const VICE_SEGRETARIO = {
  ruolo: "Vice Segretario",
  cognome: "Moscatelli",
  email: "vicesegretariolombardia@siamoesercito.org",
  foto: moscatelliFoto,
};

export const MEMBRI_ORGANIZZAZIONE = [PRESIDENTE, SEGRETARIO, VICE_SEGRETARIO];
