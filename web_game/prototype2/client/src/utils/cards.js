const SUITS = ['♠', '♥', '♣', '♦'];
const RANKS = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

function freshDeck() {
	return SUITS.flatMap(suit => {
		return RANKS.map(value => {
			return new Card(suit, value);
		});
	});
};

export class Deck {
	constructor(cards=freshDeck()) {
		this.cards = cards;
	}
	
	get len() {
		return this.cards.length;
	}
}

export class Card {
	constructor(rank, suit) {
		this.rank = rank;
		this.suit = suit;
	}
	
	get color() {
		return this.suit === "♣" || this.suit === "♠" ? "black" : "red";
	};
}

export function objectsArrayToCards(objs) {
	return objs.map(o => new Card(o['rank'], o['suit']));
}

export function objectToCard(o) {
	return new Card(o['rank'], o['suit'])
}