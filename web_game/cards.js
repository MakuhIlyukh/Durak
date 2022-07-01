const SUITS = ["♠", "♣", "♥", "♦"];
const RANKS = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"];

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

	getHTML(clickable=false, click_handler) {
		const cardDiv = document.createElement("div")
		cardDiv.innerText = this.suit
		cardDiv.classList.add("card", this.color)
		if (clickable) {
			cardDiv.style = "cursor: pointer;";
			cardDiv.addEventListener('click', click_handler);
		}
		cardDiv.dataset.value = `${this.rank}`
		return cardDiv
  	}
}

export function enemyCardsHTML(n_of_cards) {
	let l = [];
	for (let i = 0; i < n_of_cards; i++) {
		const cardDiv = document.createElement("div");
		cardDiv.innerText = "?";
		cardDiv.classList.add("card", "black");
		cardDiv.dataset.value = ``;
		l.push(cardDiv);
	}
	return l;
}