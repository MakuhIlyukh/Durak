import { useEffect } from "react";
import EnemyCardComp from "./EnemyCardComp";

function get_col(curColor) {
	console.log(curColor)
	if (curColor === 'red') return "rgb(251, 219, 219)";
	else if (curColor === 'green') return "rgb(228, 255, 239)";
	else if (curColor === 'blue') return "rgb(219, 243, 251)";
	else if (curColor === 'white') return "rgb(255, 255, 255)";
	else return "rgb(255, 255, 255)";
}

export default function EnemyCards ( {n_cards, curColor} ) {
	return (
		<div className="player1_cards grid-container marg-bot"
			 style={{"backgroundColor": get_col(curColor)}} >
			{
				[...Array(n_cards)].map((e, i) => {
					return <EnemyCardComp key={i} />;
				})
			}		
		</div>
	)
}