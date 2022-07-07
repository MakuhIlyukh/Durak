import { useRef, useState } from "react";
import { useGameInfo } from "../contexts/GameInfoProvider";
import { useSocket } from "../contexts/SocketProvider";

export default function Rooms ( {compId, setCompId} ) {
	const inpRef = useRef()
	const sockRef = useSocket()
	const gameInfo = useGameInfo()

	function onCreateRoomClick() {
		sockRef.current.emit(
			'create room',
			(response) => {
				if (response['status'] === 'ok') {
					gameInfo.current = {room_id: response['room_id']}
					setCompId(1);
				}
			})
	}
	
	function onJoinRoomClick() {
		const inputRoomId = inpRef.current.value;
		sockRef.current.emit(
			'join to room',
			{room_id: inputRoomId},
			(response) => {
				if (response['status'] === 'ok') {
					gameInfo.current = {room_id: inputRoomId}
					setCompId(1);
				} else if (response['status'] === 'bad') {
					alert(response['message'])
				}
		})
	}

	return (
		<div>
			<button onClick={ onCreateRoomClick }>
				Создать комнату
			</button>
			<input ref={inpRef}>
			</input>
			<button onClick={ onJoinRoomClick }>
				Войти в комнату
			</button>
		</div>
	);
}