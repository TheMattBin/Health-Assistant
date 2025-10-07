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
      title="Logout"
    >
      <FiLogOut />
      Logout
    </button>
  );
}
