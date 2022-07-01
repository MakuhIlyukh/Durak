import EnemyCardComp from "./EnemyCardComp";


export default function EnemyCards ( {n_cards} ) {
	return (
		<div className="player1_cards grid-container marg-bot">
			{
				[...Array(n_cards)].map((e, i) => {
					return <EnemyCardComp key={i} />;
				})
			}		
		</div>
	)
}