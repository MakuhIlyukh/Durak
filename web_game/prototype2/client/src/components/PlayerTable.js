import CardComp from "./CardComp";

export default function PlayerTable ( {player_table_cards} ) {
	return (
		<div className="player2_table grid-container marg-bot">
			{
				player_table_cards.map((e, i) => {
					return <CardComp rank={e.rank} suit={e.suit} color={e.color} key={i} />;
				})
			}		
		</div>
	)
}