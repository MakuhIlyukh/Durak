import { useState } from "react";
import Rooms from "./Rooms";
import Game from "./Game";

export default function Switcher () {
	const [compId, setCompId] = useState(0);
	
	if (compId === 0) {
		return <Rooms compId={compId} setCompId={setCompId} />
	} else {
		return <Game compId={compId} setCompId={setCompId} />
	}
}