import { Badge } from "@/components/ui/Badge";
import type { RuoloUtente } from "@/types/api";

const ETICHETTE: Record<RuoloUtente, string> = {
  amministratore: "Amministratore",
  operatore: "Operatore",
  socio: "Socio",
};

const VARIANTI: Record<RuoloUtente, "brand" | "success" | "neutral"> = {
  amministratore: "brand",
  operatore: "success",
  socio: "neutral",
};

export function RuoloBadge({ ruolo }: { ruolo: RuoloUtente }) {
  return <Badge variant={VARIANTI[ruolo]}>{ETICHETTE[ruolo]}</Badge>;
}
