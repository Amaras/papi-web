from data.tournament import Tournament
from data.player import Player
from data.util import Result, TRFResult, Color, TournamentPairing

from typing import NamedTuple


def wins(player: Player, _tournament: Tournament, max_round: int) -> int:
    """Computes the number of games where a participant obtains, with
    or without playing, as many points as awarded for a win.
    See Handbook C.07.7.1."""
    return sum(
        pairing.result.point_value == Result.GAIN
        for round_index, pairing in player.pairings.items()
        if round_index < max_round
    )


def games_won(player: Player, _tournament: Tournament, max_round: int) -> int:
    """Computes the number of games won over the board.
    See Handbook C.07.7.2."""
    return sum(
        pairing.result == Result.GAIN
        for round_index, pairing in player.pairings.items()
        if round_index < max_round
    )


def games_played_with_black(player: Player, _tourament: Tournament, max_round: int) -> int:
    """Computes the number of games played over the board with
    the black pieces.
    See Handbook C.07.7.3"""
    return sum(
        pairing.opponent_id != 1
        and pairing.result in (Result.GAIN, Result.DRAW_OR_HPB, Result.LOSS)
        and pairing.color == Color.BLACK.value
        for round_index, pairing in player.pairings.items()
        if round_index < max_round
    )


def games_won_with_black(player: Player, _tournament: Tournament, max_round: int) -> int:
    """Computes the number of games won over the board with
    the black pieces.
    See Handbook C.07.7.4
    """
    return sum(
        pairing.result == Result.GAIN and pairing.color == Color.BLACK.value
        for round_index, pairing in player.pairings.items()
        if round_index < max_round
    )


def progressive_scores(player: Player, _tournament: Tournament, max_round: int) -> int:
    """After each round a participant has a certain score.
    This tie-break is calculated adding the score of the participant at
    the end of each round.
    See Handbook C.07.7.5"""
    # NOTE(Amaras): while the documentation is the "correct" way to
    # compute this tie-break by hand, there is an easier way to compute
    # it, up to, but not including the current round.
    if max_round < 2:
        return 0
    return sum(
        (max_round - round_index) * pairing.result.point_value
        for round_index, pairing in player.pairings.items()
        if round_index < max_round
    )


def games_elected_to_play(player: Player, _tournament: Tournament, max_round: int) -> int:
    """The number of rounds, reduced by the number of half-point byes,
    zero-point byes or forfeit losses that a participant had in the tournament.
    See Handbook C.07.7.6"""
    return len(
        [
            pairing.opponent_id != 1
            and pairing.result not in (
                Result.FORFEIT_LOSS,
                Result.DOUBLE_FORFEIT,
                Result.NOT_PAIRED
            )
            for round_index, pairing in player.pairings.items()
            if round_index < max_round
        ]
    )


class RoundScore(NamedTuple):
    round_index: int
    point_value: float
    voluntary_unplayed: bool


def buchholz(
        player: Player,
        tournament: Tournament,
        max_round: int,
        *, cut: int = 0) -> float:
    if cut < 0:
        raise ValueError(f"Cannot cut negative values, got: {cut}")
    if cut > 0:
        raise NotImplementedError("TODO: allow cut")
    if tournament.pairing == TournamentPairing.BERGER:
        score = 0
        current_round = tournament.current_round
        for round_index, pairing in player.pairings.items():
            opponent: Player = tournament.players_by_id[pairing.opponent_id]
            score += opponent.points_before_round(current_round)
        return score
    raise NotImplementedError("TODO: Buchholz for Swiss tournaments")
