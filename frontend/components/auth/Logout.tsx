import { useRouter } from "next/router";
import { FiLogOut } from "react-icons/fi";

export default function Logout() {
  const router = useRouter();
  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };
  return (
    <button
      onClick={handleLogout}
      style={{
        background: "none",
        border: "none",
        color: "#b0b3b8",
        cursor: "pointer",
        marginLeft: 12,
        fontSize: 22,
        verticalAlign: "middle",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 0,
      }}
      title="Logout"
    >
      <FiLogOut />
    </button>
  );
}
