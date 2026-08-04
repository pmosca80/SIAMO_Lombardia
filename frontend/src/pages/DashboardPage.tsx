import { Megaphone, Send, Users } from "lucide-react";
import { Card, CardBody } from "@/components/ui/Card";
import { useUtenti } from "@/api/utenti";
import { useComunicazioni } from "@/api/comunicazioni";

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users;
  label: string;
  value: number | string;
}) {
  return (
    <Card>
      <CardBody className="flex items-center gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-md bg-brand-50 text-brand-600">
          <Icon size={20} />
        </div>
        <div>
          <p className="text-2xl font-semibold text-brand-950">{value}</p>
          <p className="text-sm text-brand-950/60">{label}</p>
        </div>
      </CardBody>
    </Card>
  );
}

export function DashboardPage() {
  const { data: utenti } = useUtenti();
  const { data: comunicazioni } = useComunicazioni();

  const inviate = comunicazioni?.filter((c) => c.stato === "inviata").length ?? 0;
  const bozze = comunicazioni?.filter((c) => c.stato === "bozza").length ?? 0;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-brand-950">Dashboard</h1>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={Users} label="Soci attivi" value={utenti?.filter((u) => u.attivo).length ?? "—"} />
        <StatCard icon={Send} label="Comunicazioni inviate" value={comunicazioni ? inviate : "—"} />
        <StatCard icon={Megaphone} label="Bozze in preparazione" value={comunicazioni ? bozze : "—"} />
      </div>
    </div>
  );
}
