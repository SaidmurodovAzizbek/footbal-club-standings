from sqladmin import ModelView
from app.models.league import League
from app.models.club import Club
from app.models.match import Match
from app.models.standing import Standing

class LeagueAdmin(ModelView, model=League):
    column_list = [League.id, League.name_en, League.country, League.code, League.is_active]
    column_searchable_list = [League.name_en, League.code, League.country]
    column_sortable_list = [League.id, League.name_en, League.is_active]
    name_plural = "Leagues"
    icon = "fa-solid fa-trophy"

class ClubAdmin(ModelView, model=Club):
    column_list = [Club.id, Club.name_en, Club.short_name, Club.tla, Club.founded, Club.league_id]
    column_searchable_list = [Club.name_en, Club.short_name, Club.tla]
    column_sortable_list = [Club.id, Club.name_en, Club.founded]
    name_plural = "Clubs"
    icon = "fa-solid fa-shield-halved"

class MatchAdmin(ModelView, model=Match):
    column_list = [Match.id, Match.matchday, Match.home_team_id, Match.away_team_id, Match.status, Match.utc_date]
    column_searchable_list = [Match.status]
    column_sortable_list = [Match.utc_date, Match.matchday, Match.status]
    name_plural = "Matches"
    icon = "fa-solid fa-futbol"

class StandingAdmin(ModelView, model=Standing):
    column_list = [Standing.id, Standing.league_id, Standing.club_id, Standing.position, Standing.points, Standing.played]
    column_searchable_list = [Standing.form]
    column_sortable_list = [Standing.position, Standing.points]
    name_plural = "Standings"
    icon = "fa-solid fa-list-ol"
