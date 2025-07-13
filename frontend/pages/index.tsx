import React from "react";
import MedicalChat from "../components/chat/MedicalChat";
import Logout from "../components/auth/Logout";

export default function Home() {
  return <MedicalChat LogoutButton={Logout} />;
}
