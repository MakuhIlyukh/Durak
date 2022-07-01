import CardComp from "./CardComp";

export default function EnemyTable ( {enemy_table_cards} ) {
	return (
		<div className="player1_table grid-container">
			{
				enemy_table_cards.map((e, i) => {
					return <CardComp rank={e.rank} suit={e.suit} color={e.color} key={i} />;
				})
			}		
		</div>
	)
}