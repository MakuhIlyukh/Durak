import CardComp from "./CardComp";

export default function PlayerCards ( {player_cards, click_handler, curColor} ) {
	function get_col(curColor) {
		console.log(curColor)
		if (curColor === 'red') return "rgb(251, 219, 219)";
		else if (curColor === 'green') return "rgb(228, 255, 239)";
		else if (curColor === 'blue') return "rgb(219, 243, 251)";
		else if (curColor === 'white') return "rgb(255, 255, 255)";
		else return "rgb(255, 255, 255)";
	}
	return (
		<div className="player2_cards grid-container"
		 	 style={{"backgroundColor": get_col(curColor)}}>
			{
				player_cards.map((e, i) => {
					return <CardComp rank={e.rank}
									 suit={e.suit}
									 color={e.color}
									 key={i}
									 clickable={true}
									 click_handler={click_handler}/>;
				})
			}	
		</div>
	)
}