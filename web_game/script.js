import { Deck, Card, enemyCardsHTML } from "./cards.js";


function renderCards(cards, element) {
	element.innerHTML = "";
	for (let i = 0; i < cards.length; i++) {
		element.appendChild(cards[i]);
	}
}

function renderDeckSize(size) {
	deckSizeElement.innerHTML = +size;
}

function cardClickHandler(e) {
	let rank = e.target.dataset.value;
	let suit = e.target.innerText;

	if (suit === 'FINISH') {
		console.log(["FINISH", null]);
	} else {
		console.log(["PUT", new Card(rank, suit)]);
	}
};


const p1CardsElement = document.querySelector(".player1_cards");
const p2CardsElement = document.querySelector(".player2_cards");
const p1TableElement = document.querySelector(".player1_table");
const p2TableElement = document.querySelector(".player2_table")
const trumpElement = document.querySelector(".trump");
const deckSizeElement = document.querySelector(".deck-size");

let enemyCardsHTMLS = enemyCardsHTML(7);
let playerCardsHTMLS = [
	new Card('J', '♣'),
	new Card('K', '♠'),
	new Card('10', '♥'),
	new Card('A', '♦'),
	new Card('', 'FINISH'),
].map(x => x.getHTML(true, cardClickHandler));
let enemyTableHTMLS = [
	new Card('7', '♣'),
	new Card('9', '♠'),
	new Card('J', '♥'),
	new Card('K', '♦')
].map(x => x.getHTML());
let playerTableHTMLS = [
	new Card('6', '♣'),
	new Card('7', '♠'),
	new Card('8', '♥'),
	new Card('9', '♦')
].map(x => x.getHTML());

let trumpCardHTML = new Card('8', '♦').getHTML();

renderCards(enemyCardsHTMLS, p1CardsElement);
renderCards(playerCardsHTMLS, p2CardsElement);
renderCards([trumpCardHTML], trumpElement);
renderCards(enemyTableHTMLS, p1TableElement);
renderCards(playerTableHTMLS, p2TableElement);
renderDeckSize(15);