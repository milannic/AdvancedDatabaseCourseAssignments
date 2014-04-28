#! /usr/bin/python

import re
import sys
import argparse
import json
import uuid
import urllib
from operator import itemgetter, attrgetter

query_type = -1
query = ""
freeBase_key = "none"
#type_dict = {
#"/people/person":'Person',
#"/book/author":"Author",
#"/film/actor":"Actor",
#"/tv/tv_actor":"Actor",
#"/organization/organization_founder":"BusinessPerson",
#"/business/board_member":"BusinessPerson",
#"/sports/sports_league":"League",
#"/sports/sports_team":"League",
#"/sports/professional_sports_team":"SportsTeam",
#}



info_dict = {}


def validateType(type_string):
    global query_type
    if re.match("^infobox$",type_string) == None:
        if re.match("^question$",type_string) == None:
            print "your query type is not correct,either infobox or question"
            sys.exit(1)
        else:
            query_type = 1;
    else:
        query_type = 0;


def getInfobox(query):
    global freeBase_key

    info_dict = {}

    type_dict = {
        "Actor": 0 ,
        "Author": 0 ,
        "League": 0 ,
        "BusinessPerson": 0 ,
        "SportsTeam": 0,
    }

    service_url_topic = 'https://www.googleapis.com/freebase/v1/topic'
    service_url_search = 'https://www.googleapis.com/freebase/v1/search'


    params = {
      'query' : query,
      'key': freeBase_key,
      'indent': 'true'
    }
    url = service_url_search + '?' + urllib.urlencode(params)


#        print url
#
#        print query

    response = json.loads(urllib.urlopen(url).read())
    #print response

    #haha=raw_input("---------------------------")
    if not response['result']:
        print "No Such Topic"
        return
        #sys.exit(1)

    for result in response['result']:
        #print result['name'] + ' (' + str(result['score']) + ')'
        #print result['mid']
        try:
            topic_id = result['mid']
            break
        except:
            print "No Such Topic"
            return
            #sys.exit(1)

    params = {
      'key': freeBase_key,
      'filter': "all",
      'indent': 'true'
    }
    url = service_url_topic + topic_id + '?' + urllib.urlencode(params)
    #print url

    topic = json.loads(urllib.urlopen(url).read())
    #print topic

    #haha=raw_input("---------------------------")
#    with open("json_output","w") as output:
#        json.dump(topic,output,indent=4)


    for property in topic['property']:
        #print property + ":"

# Name for all the roles

        if re.match('/type/object/name',property):
            name_list = []
            for value in topic['property'][property]['values']:
                name_list.append(str(value['text'].encode("ascii","ignore")))
            if len(name_list) != 0:
                info_dict['Name'] = name_list

# Description for all the roles

        if re.match('/common/topic/description',property):
            description_list = []
            for value in topic['property'][property]['values']:
                description_list.append(value['value'].replace(u'\u2013',u'-').encode("ascii","ignore"))
            if description_list:
                info_dict['Description'] = description_list
# Slogan nowhere to put
        if re.match('/organization/organization/slogan',property):
            if  topic['property'][property]['values']:
                slogan_list = []
                for value in topic['property'][property]['values']:
                    slogan_list.append(str(value['value'].encode("ascii","ignore")))
                if slogan_list:
                    info_dict['Slogan']=slogan_list
# Official website
        if re.match('/common/topic/official_website',property):
            if  topic['property'][property]['values']:
                website_list = []
                for value in topic['property'][property]['values']:
                    website_list.append(str(value['value'].encode("ascii","ignore")))
                if website_list:
                    info_dict['Official Website']=website_list
# Birthday for Person : date_of_birth

        if re.match('.*date_of_birth',property):
            date_of_birth_list = []
            for value in topic['property'][property]['values']:
                date_of_birth_list.append(str(value['text'].encode("ascii","ignore")))
            if date_of_birth_list:
                info_dict['Birthday']=date_of_birth_list

# Place Of Birth for Person : place_of_birth

        if re.match('.*place_of_birth',property):
            place_of_birth_list = []
            for value in topic['property'][property]['values']:
                place_of_birth_list.append(str(value['text'].encode("ascii","ignore")))
            if place_of_birth_list:
                info_dict['Place Of Birth']=place_of_birth_list


# Cause Of Death for Person : cause_of_death

        if re.match('.*cause_of_death',property):
            cause_of_death_list = []
            for value in topic['property'][property]['values']:
                cause_of_death_list.append(str(value['text'].encode("ascii","ignore")))
            if cause_of_death_list :
                info_dict['Cause Of Death'] = cause_of_death_list

# Date Of Death for Person : place_of_birth

        if re.match('.*date_of_death',property):
            date_of_death_list = []
            for value in topic['property'][property]['values']:
                date_of_death_list.append(str(value['text'].encode("ascii","ignore")))
            if date_of_death_list:
                info_dict['Date Of Death'] = date_of_death_list

# Place Of Death for Person : place_of_death

        if re.match('.*place_of_death',property):
            place_of_death_list = []
            for value in topic['property'][property]['values']:
                place_of_death_list.append(str(value['text'].encode("ascii","ignore")))
            if place_of_death_list:
                info_dict['Place Of Death'] = place_of_death_list

# Siblings : sibling_s

        if re.match(r'.*sibling_s',property):
            sibling_s_list = []
            for value in topic['property'][property]['values']:
                for next_value in value['property']['/people/sibling_relationship/sibling']['values']:
                    sibling_s_list.append(str(next_value['text'].encode("ascii","ignore")))
            if sibling_s_list:
                info_dict['Siblings'] = sibling_s_list

# Spouses : spouse_s

        if re.match(r'.*spouse_s',property):
            spouse_s_list = []
            for value in topic['property'][property]['values']:
                if value['property'].has_key("/people/marriage/spouse"):
                    name_m = value['property']['/people/marriage/spouse']['count']!=0 and value['property']['/people/marriage/spouse']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    name_m = ''
                if value['property'].has_key('/people/marriage/type_of_union'):
                    type_m = value['property']['/people/marriage/type_of_union']['count']!=0 and value['property']['/people/marriage/type_of_union']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    type_m = ''
                if value['property'].has_key('/people/marriage/location_of_ceremony'):
                    location_m = value['property']['/people/marriage/location_of_ceremony']['count']!=0 and (" @ " + value['property']['/people/marriage/location_of_ceremony']['values'][0]['text'].encode("ascii","ignore")) or ''
                else:
                    location_m = ''
                if value['property'].has_key('/people/marriage/to'):
                    to_m = value['property']['/people/marriage/to']['count']!=0 and value['property']['/people/marriage/to']['values'][0]['text'].encode("ascii","ignore") or 'Now'
                else:
                    to_m = ''
                if value['property'].has_key('/people/marriage/from'):
                    from_m = value['property']['/people/marriage/from']['count']!=0 and value['property']['/people/marriage/from']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    from_m = ''
                spouse_s_list.append(name_m +" (" + from_m + " - " + to_m + " ) " + location_m)
            if spouse_s_list:
                info_dict['Spouses'] = spouse_s_list

# Books : works_written
        if re.match(r'.*author\/works_written',property):
            if topic['property'][property]['count'] != 0:
                type_dict['Author'] = 1;
            works_written_list = []
            for value in topic['property'][property]['values']:
                works_written_list.append(value['text'].encode("ascii","ignore"))
            if works_written_list:
                info_dict['Books'] = works_written_list

# Books About : book_subject/works
        if re.match(r'.*book\_subject\/works',property):
            works_list = []
            if topic['property'][property]['count'] != 0:
                type_dict['Author'] = 1;
            for value in topic['property'][property]['values']:
                works_list.append(value['text'].encode("ascii","ignore"))
            if works_list:
                info_dict['Books About'] = works_list

# Influenced : influenced
        if re.match(r'.*influenced$',property):
            influenced_list = []
#                if topic['property'][property]['count'] != 0:
#                    type_dict['Author'] = 1;
            for value in topic['property'][property]['values']:
                influenced_list.append(str(value['text'].encode("ascii","ignore")))
            if influenced_list:
                info_dict['Influenced'] = influenced_list

# Influenced By : influenced_by
        if re.match(r'.*influenced_by',property):
            influenced_by_list=[]
#                if topic['property'][property]['count'] != 0:
#                    type_dict['Author'] = 1;
            for value in topic['property'][property]['values']:
                influenced_by_list.append(str(value['text'].encode("ascii","ignore")))
            if influenced_by_list:
                info_dict['Influenced By'] = influenced_by_list

# Film : /film/actor/film
        if re.match(r'.*actor\/film$',property):
            if topic['property'][property]['count'] != 0:
                type_dict['Actor'] = 1;
            film_list = [('Character',"Film Name")]
            for value in topic['property'][property]['values']:
                if value['property'].has_key('/film/performance/character'):
                    character = value['property']['/film/performance/character']['values'] and value['property']['/film/performance/character']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    character = ""
                if value['property'].has_key('/film/performance/film'):
                    film = value['property']['/film/performance/film']['values'] and value['property']['/film/performance/film']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    film = ""
                film_list.append((character,film))
            if len(film_list) != 1:
                info_dict['Films'] = film_list


# TV Starring Roles : /tv/tv_actor/starring_roles
        if re.match(r'.*actor\/starring\_roles$',property):

            if topic['property'][property]['count'] != 0:
                type_dict['Actor'] = 1;

            tv_starring=[("Character","TV")]

            #print property

            for value in topic['property'][property]['values']:
                #print value['property']
                if value['property'].has_key('/tv/regular_tv_appearance/character'):
                    tv_starring_roles=value['property']['/tv/regular_tv_appearance/character']['values'] and value['property']['/tv/regular_tv_appearance/character']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    tv_starring_roles = ''
                if value['property'].has_key('/tv/regular_tv_appearance/series'):
                    tv_starring_name=value['property']['/tv/regular_tv_appearance/series']['values'] and value['property']['/tv/regular_tv_appearance/series']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    tv_starring_name = value['property']['/type/object/type']['values'][0]['text'].encode("ascii","ignore")
                tv_starring.append((tv_starring_roles,tv_starring_name))
            if len(tv_starring)!=1:
                info_dict['TV Starring'] = tv_starring


# TV Guest Roles : /tv/tv_actor/guest_roles
        if re.match(r'.*actor\/guest\_roles$',property):

            if topic['property'][property]['count'] != 0:
                type_dict['Actor'] = 1;

            tv_guest=[("Character","TV")]

            for value in topic['property'][property]['values']:
                if value['property'].has_key('/tv/tv_guest_role/character'):
                    tv_guest_role=value['property']['/tv/tv_guest_role/character']['values'] and value['property']['/tv/tv_guest_role/character']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    tv_guest_role = ''
                if value['property'].has_key('/tv/tv_guest_role/episodes_appeared_in'):
                    tv_guest_name=value['property']['/tv/tv_guest_role/episodes_appeared_in']['values'] and value['property']['/tv/tv_guest_role/episodes_appeared_in']['values'][0]['text'].encode("ascii","ignore") or ''
                else:
                    tv_guest_name = value['property']['/type/object/type']['values'][0]['text'].encode("ascii","ignore")
                tv_guest.append((tv_guest_role,tv_guest_name))
            if len(tv_guest)!=1:
                info_dict['TV Guest'] = tv_guest

        if re.match('/business/board_member',property) or re.match('/organization/organization_founder/organizations_founded',property):
            type_dict['BusinessPerson'] = 1;
            busi_found_list =[]
            busi_leader_list =[]
            busi_member_list = []
#Organization that found
            if re.match('/organization/organization_founder/organizations_founded',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        busi_found_list.append(str(value['text'].encode("ascii","ignore")))
                    if busi_found_list:
                        info_dict['Founded'] = busi_found_list
#leadership list, index 0-4 mapping from,name,role,title,to
            if re.match('/business/board_member/leader_of',property):
                busi_leader_list = [("Organization","Role","Title","From/To")]
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        leadership = []
                        if '/organization/leadership/organization' in value['property']:
                            if value['property']['/organization/leadership/organization']['values']:
                                leadership.append(str(value['property']['/organization/leadership/organization']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                leadership.append(str(''))
                        else:
                            leadership.append(str(''))
                        if '/organization/leadership/role' in value['property']:
                            if value['property']['/organization/leadership/role']['values']:
                                leadership.append(str(value['property']['/organization/leadership/role']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                leadership.append(str(''))
                        else:
                            leadership.append(str(''))
                        if '/organization/leadership/title' in value['property']:
                            if value['property']['/organization/leadership/title']['values']:
                                leadership.append(str(value['property']['/organization/leadership/title']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                leadership.append(str(''))
                        else:
                            leadership.append(str(''))
                        if '/organization/leadership/from' in value['property']:
                            if value['property']['/organization/leadership/from']['values']:
                                from_string = str(value['property']['/organization/leadership/from']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                                from_string = ""
                        else:
                                from_string = ""
                        if '/organization/leadership/to' in value['property']:
                            if value['property']['/organization/leadership/to']['values']:
                                to_string = str(value['property']['/organization/leadership/to']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                                to_string = ""
                        else:
                            to_string = ""
                        if not from_string and not to_string:
                            leadership.append("")
                        else:
                            if not from_string:
                                leadership.append(" / "+to_string)
                            if not to_string:
                                leadership.append(from_string+ " / Now")
                            else:
                                leadership.append(from_string+ " / " + to_string)
                        busi_leader_list.append(leadership)
                    if len(busi_leader_list) != 1:
                        info_dict['Leadership'] = busi_leader_list
#board membership list, index 0-4 mapping from,title,role,name,to
            if re.match('/business/board_member/organization_board_memberships',property):
                busi_member_list = [("Organization","Role","Title","From/To")]
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        board_member = []
                        if '/organization/organization_board_membership/organization' in value['property']:
                            if value['property']['/organization/organization_board_membership/organization']['values']:
                                board_member.append(str(value['property']['/organization/organization_board_membership/organization']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                board_member.append(str(''))
                        else:
                            board_member.append(str(''))
                        if '/organization/organization_board_membership/role' in value['property']:
                            if value['property']['/organization/organization_board_membership/role']['values']:
                                board_member.append(str(value['property']['/organization/organization_board_membership/role']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                board_member.append(str(''))
                        else:
                            board_member.append(str(''))
                        if '/organization/organization_board_membership/title' in value['property']:
                            if value['property']['/organization/organization_board_membership/title']['values']:
                                board_member.append(str(value['property']['/organization/organization_board_membership/title']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                board_member.append(str(''))
                        else:
                            board_member.append(str(''))
                        if '/organization/organization_board_membership/from' in value['property']:
                            if value['property']['/organization/organization_board_membership/from']['values']:
                               from_string = str(value['property']['/organization/organization_board_membership/from']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                               from_string = ""
                        else:
                               from_string = ""
                        if '/organization/organization_board_membership/to' in value['property']:
                            if value['property']['/organization/organization_board_membership/to']['values']:
                               to_string = str(value['property']['/organization/organization_board_membership/to']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                               to_string = ""
                        else:
                               to_string = ""
                        if not from_string and not to_string:
                            board_member.append("")
                        else:
                            if not from_string:
                                board_member.append(" / "+to_string)
                            if not to_string:
                                board_member.append(from_string+ " / Now")
                            else:
                                board_member.append(from_string+ " / " + to_string)
                        busi_member_list.append(board_member);
                    if len(busi_member_list)!=1:
                        info_dict['Board Membership'] =  busi_member_list
        if re.match('/sports/sports_league/',property) or re.match('/sports/professional_sports_team',property):
            type_dict['League'] = 1;
            league_sport_list =[]
            league_champion_list=[]
            team_coach_list = []
            league_team_list = []
# Sport type
            if re.match('/sports/sports_league/sport',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        league_sport = str(value['text'].encode("ascii","ignore"))
                        league_sport_list.append(league_sport)
                    if league_sport_list:
                        info_dict['League Sport'] = league_sport_list
# League championship
            if re.match('/sports/sports_league/championship',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        league_champion = str(value['text'].encode("ascii","ignore"))
                        league_champion_list.append(league_champion)
                    if league_champion_list :
                        info_dict['Championship'] = league_champion_list
# League team
            if re.match('/sports/sports_league/teams',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        if '/sports/sports_league_participation/team' in value['property']:
                            if value['property']['/sports/sports_league_participation/team']['values']:
                                league_team_list.append(value['property']['/sports/sports_league_participation/team']['values'][0]['text'].encode("ascii","ignore"))
                    if league_team_list:
                        info_dict['Teams'] = league_team_list
        if re.match('/sports/sports_team',property):
            type_dict['SportsTeam'] = 1;
            team_arena_list =[]
            team_champion_list=[]
            team_found_list = []
            team_location_list = []
            if re.match('/sports/sports_team/league',property):
                team_league_list = []
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        if '/sports/sports_league_participation/league' in value['property']:
                            if value['property']['/sports/sports_league_participation/league']['values']:
                                team_league_list.append(value['property']['/sports/sports_league_participation/league']['values'][0]['text'].encode("ascii","ignore"))
                if team_league_list:
                    info_dict['League'] = team_league_list

            if re.match('/sports/sports_team/sport',property):
                team_sport_list = []
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        team_sport = str(value['text'].encode("ascii","ignore"))
                        team_sport_list.append(team_sport)
                    if team_sport_list:
                        info_dict['Team Sport'] = team_sport_list

            if re.match('/sports/sports_team/arena_stadium',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        team_arena_list.append(str(value['text'].encode("ascii","ignore")))
                    if team_arena_list:
                        info_dict['Arena'] = team_arena_list
            if re.match('/sports/sports_team/championships',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        team_champion_list.append(str(value['text'].encode("ascii","ignore")))
                    if team_champion_list:
                        info_dict['Championships'] = team_champion_list
# Coaches
            if re.match('/sports/sports_team/coaches',property):
                team_coach_list = [["Name","Position","From/To"]]
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        coach_info = []
                        if '/sports/sports_team_coach_tenure/coach' in value['property']:
                            if value['property']['/sports/sports_team_coach_tenure/coach']['values']:
                                coach_info.append(str(value['property']['/sports/sports_team_coach_tenure/coach']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                coach_info.append(str(''))
                        else:
                            coach_info.append(str(''))
                        if '/sports/sports_team_coach_tenure/position' in value['property']:
                            if value['property']['/sports/sports_team_coach_tenure/position']['values']:
                                coach_info.append(str(value['property']['/sports/sports_team_coach_tenure/position']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                coach_info.append(str(''))
                        else:
                            coach_info.append(str(''))
                        if '/sports/sports_team_coach_tenure/from' in value['property']:
                            if value['property']['/sports/sports_team_coach_tenure/from']['values']:
                                 from_string = str(value['property']['/sports/sports_team_coach_tenure/from']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                                from_string = ""
                        else:
                            from_string = ""
                        if '/sports/sports_team_coach_tenure/to' in value['property']:
                            if value['property']['/sports/sports_team_coach_tenure/to']['values']:
                                to_string = str(value['property']['/sports/sports_team_coach_tenure/to']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                                to_string = ""
                        else:
                            to_string = ""
                        if not from_string and not to_string:
                            coach_info.append("")
                        else:
                            if not from_string:
                                coach_info.append(" / "+to_string)
                            if not to_string:
                                coach_info.append(from_string+ " / Now")
                            else:
                                coach_info.append(from_string+ " / " + to_string)
                        team_coach_list.append(coach_info);
                    if len(team_coach_list)!= 1:
                        info_dict['Coaches'] =  team_coach_list
            if re.match('/sports/sports_team/founded',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        team_found_list.append(str(value['text'].encode("ascii","ignore")))
                    if team_found_list:
                        info_dict['Founded'] = team_found_list
            if re.match('/sports/sports_team/location',property):
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        team_location_list.append(str(value['text'].encode("ascii","ignore")))
                    if team_location_list:
                        info_dict['Locations'] = team_location_list
            if re.match('/sports/sports_team/league',property):
                team_league_list = []
                if topic['property'][property]['values']:
                        for value in topic['property'][property]['values']:
                            if '/sports/sports_league_participation/league' in value['property']:
                                if value['property']['/sports/sports_league_participation/league']['values']:
                                    team_league_list.append(str(value['property']['/sports/sports_league_participation/league']['values'][0]['text'].encode("ascii","ignore")))
                        if team_league_list:
                            info_dict['Leagues'] = team_league_list
            if re.match('/sports/sports_team/roster',property):
                team_roster_list = [["Name","Position","Number","From/To"]]
                if topic['property'][property]['values']:
                    for value in topic['property'][property]['values']:
                        roster_member = []
                        if '/sports/sports_team_roster/player' in value['property']:
                            if value['property']['/sports/sports_team_roster/player']['values']:
                                roster_member.append(str(value['property']['/sports/sports_team_roster/player']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                roster_member.append(str(''))
                        else:
                            roster_member.append(str(''))
                        if '/sports/sports_team_roster/position' in value['property']:
                            temp = ''
                            for position in value['property']['/sports/sports_team_roster/position']['values']:
                                temp = temp +str(position['text'].encode("ascii","ignore"))+' ,'
                            roster_member.append(temp[0:len(temp)-1])
                        else:
                            roster_member.append(str(''))
                        if '/sports/sports_team_roster/number' in value['property']:
                            if value['property']['/sports/sports_team_roster/number']['values']:
                                roster_member.append(str(value['property']['/sports/sports_team_roster/number']['values'][0]['text'].encode("ascii","ignore")))
                            else:
                                roster_member.append(str(''))
                        else:
                            roster_member.append(str(''))
                        if '/sports/sports_team_roster/from' in value['property']:
                            if value['property']['/sports/sports_team_roster/from']['values']:
                                from_string = str(value['property']['/sports/sports_team_roster/from']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                                from_string = ""
                        else:
                            from_string = ""
                        if '/sports/sports_team_roster/to' in value['property']:
                            if value['property']['/sports/sports_team_roster/to']['values']:
                                to_string = str(value['property']['/sports/sports_team_roster/to']['values'][0]['text'].encode("ascii","ignore"))
                            else:
                                to_string = ""
                        else:
                            to_string = ""

                        if not from_string and not to_string:
                            roster_member.append("")
                        else:
                            if not from_string:
                                roster_member.append(" / "+to_string)
                            if not to_string:
                                roster_member.append(from_string+ " / ")
                            else:
                                roster_member.append(from_string+ " / " + to_string)
                        team_roster_list.append(roster_member);
                    if len(team_roster_list)!=1:
                        info_dict['PlayersRoster'] =  team_roster_list






    temp = ''
    if type_dict["League"] == 1 and type_dict["SportsTeam"] ==1:
        type_dict["League"] = 0
    if type_dict["League"] == 1 or type_dict["SportsTeam"] ==1:
        type_dict["Author"] = 0
        type_dict["Actor"] = 0
        type_dict["BusinessPerson"] = 0

    for keys in type_dict.keys():
        if type_dict[keys] == 1:
            if temp:
                temp = temp + " " + keys
            else:
                temp = keys
    if temp:
        temp = "(" + temp + ")"
        my_list = []
        my_list.append(info_dict['Name'][0]+temp)
        info_dict['HeadName']= my_list
    else:
        try:
            info_dict['HeadName'] = info_dict['Name']
        except:
            print "No Avaliable Info"
    return (info_dict,type_dict)


def displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,dis_type,filed_name,column):
#dis_type = 0 means Head Format
    if dis_type == 0:
        if info_dict.has_key(filed_name):
            print line_sep*max_line_length
            head_len = len(info_dict[filed_name][0])
            start_point = (max_line_length-head_len)/2
            if (max_line_length-head_len)%2 == 0 :
                print row_sep + " "*(start_point-1) + info_dict[filed_name][0] + " "*(start_point)+row_sep
            else:
                print row_sep + " "*(start_point-1) + info_dict[filed_name][0] + " "*(start_point+1)+row_sep
            print line_sep*max_line_length
#dis_type = 1 means One Line Format
    elif dis_type == 1:
        if info_dict.has_key(filed_name):
            content = info_dict[filed_name][0]
            first_blank = head_column_length-len(" "+filed_name+":")-1
            second_blank =(max_line_length - head_column_length - len(content)) > 0 and (max_line_length - head_column_length - len(content)) or 0
            if not second_blank :
                content = content[0:max_line_length-head_column_length]
            if filed_name == "League Sport" or filed_name == "Team Sport":
                filed_name = "Sport"
                first_blank = head_column_length-len(" "+filed_name+":")-1
            print row_sep + " "+filed_name+":" + " " * first_blank + content + " "*second_blank + row_sep
            print line_sep*max_line_length

#dis_type = 2 means Simply Multi-values
    elif dis_type == 2:
        if info_dict.has_key(filed_name):
            for i in xrange(len(info_dict[filed_name])):
                if i == 0:
                    content = info_dict[filed_name][i]
                    first_blank = head_column_length-len(" "+filed_name+":")-1
                    second_blank =(max_line_length - head_column_length - len(content)) > 0 and (max_line_length - head_column_length - len(content)) or 0
                    if not second_blank :
                        content = content[0:max_line_length-head_column_length-3]+"..."
                    print row_sep + " "+filed_name+":" + " " * first_blank + content + " "*second_blank + row_sep
                else:
                    content = info_dict[filed_name][i]
                    second_blank =(max_line_length - head_column_length - len(content)) > 0 and (max_line_length - head_column_length - len(content)) or 0
                    if not second_blank :
                        content = content[0:max_line_length-head_column_length-3]+"..."
                    print row_sep + " "*(head_column_length-1) + content + " "*second_blank + row_sep


            print line_sep*max_line_length
#dis_type = 3 actually this is only for Description
    elif dis_type == 3:
        if info_dict.has_key(filed_name):
            content = info_dict[filed_name][0]
            content = content.replace("\n","")
            first_blank = head_column_length-len(" "+filed_name+":")-1
            second_blank =(max_line_length - head_column_length - len(content)) > 0 and (max_line_length - head_column_length - len(content)) or 0
            multi = 0
            if not second_blank :
                multi = 1
            print row_sep + " "+filed_name+":" + " " * first_blank + content[0:max_line_length-head_column_length] + " "*second_blank + row_sep
            if multi:
                cur = max_line_length - head_column_length
                total_len = len(content)
                while cur<total_len:
                    if cur+max_line_length-head_column_length <= total_len:
                        print row_sep + " "*(head_column_length-1) + content[cur:cur+max_line_length-head_column_length] + " "*second_blank + row_sep
                    else:
                        print row_sep + " "*(head_column_length-1) + content[cur:total_len] + " "*second_blank +" "*(cur+max_line_length-head_column_length-total_len)+ row_sep
                    cur = cur+max_line_length-head_column_length

            print line_sep*max_line_length

#Three Line Additional table
    elif dis_type == 4:
        if column ==3:
            subcolumn_length = (max_line_length-head_column_length)/column +1
        elif column ==4 :
            subcolumn_length = (max_line_length-head_column_length)/column
        elif column == 2 :
            subcolumn_length = (max_line_length-head_column_length)/column
        else:
            subcolumn_length = (max_line_length-head_column_length)/column +1
        if info_dict.has_key(filed_name):
            for i in xrange(len(info_dict[filed_name])):
                content = info_dict[filed_name][i]
                if i == 0:
                    first_blank = head_column_length-len(" "+filed_name+":")-2
                    headstring = row_sep+" "+filed_name+":"+" "*(first_blank)+row_sep
                    for j in xrange(column):
                        # one for the space
                        temp = ""
                        if len(content[j])+1 >= subcolumn_length:
                            temp = content[j][0:subcolumn_length-4] + "... "
                            blank = 0
                        else:
                            blank = (subcolumn_length-len(content[j])-1)
                            temp = content[j]
                        if j==0:
                            headstring = headstring + temp + " "*blank + row_sep
                        else:
                            headstring = headstring + " "+temp + " "*(blank-1) + row_sep
                    if column == 4 or column ==2:
                        headstring = headstring[0:len(headstring)-1]
                        headstring = headstring + " " + row_sep
                    print headstring
                    print " "*(head_column_length-1)+line_sep*(max_line_length-head_column_length+1)
                else:
                    headstring = row_sep+" "*(head_column_length-2)+row_sep
                    for j in xrange(column):
                        # one for the space
                        temp = ""
                        if len(content[j])+1 >= subcolumn_length:
                            temp = content[j][0:subcolumn_length-5] + "..."
                            blank = 0
                        else:
                            blank = (subcolumn_length-len(content[j])-1)
                            temp = content[j]
                        if j==0:
                            if len(content[j])+1 >= subcolumn_length:
                                headstring = headstring + temp + " "*(blank+1) + row_sep
                            else:
                                headstring = headstring + temp + " "*(blank) + row_sep
                        else:
                            headstring = headstring +" "+temp + " "*(blank-1) + row_sep

                    if column == 4 or column == 2:
                        headstring = headstring[0:len(headstring)-1]
                        headstring = headstring + " " + row_sep
                    print headstring
            print line_sep*(max_line_length)


def displayInfobox(info_dict,type_dict):
    max_line_length = 100
    head_column_length = 20
    line_sep = "-"
    row_sep = "|"
    #print start_point
    # NBA
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,0,"HeadName",0)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Name",0)
    if type_dict["League"] == 1 or type_dict["SportsTeam"] == 1:
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Team Sport",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"League Sport",0)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Birthday",0)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Place Of Birth",0)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Date Of Death",0)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Cause Of Death",0)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Place Of Death",0)
    if type_dict["League"] == 1 or type_dict["SportsTeam"] == 1:
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Slogan",0)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Official Website",0)
    if type_dict["League"] == 1 or type_dict["SportsTeam"] == 1:
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Championship",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Teams",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Arena",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Championships",0)
    if type_dict["League"] == 1 or type_dict["SportsTeam"] == 1:
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Founded",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,1,"Leagues",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Locations",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,4,"Coaches",3)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,4,"PlayersRoster",4)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,3,"Description",0)
    if not(type_dict["League"] == 1 or type_dict["SportsTeam"] == 1):
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Siblings",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Spouses",0)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,4,"Films",2)
#        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,4,"TV Starring",2)
#        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,4,"TV Guest",2)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Books",2)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Books About",2)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Influenced",2)
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Influenced By",2)
    if type_dict["League"] == 0 and type_dict["SportsTeam"] == 0:
        displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,2,"Founded",2)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,4,"Leadership",4)
    displayfield(info_dict,max_line_length,head_column_length,line_sep,row_sep,4,"Board Membership",4)

    #Process Name


#    for keys in info_dict.keys():
#        print keys+':'
#        for value in info_dict[keys]:
#            print '*************************'
#            print value
#        print '---------------------------------------------------------------'
#    pass


def getQuestion(query):
    global freeBase_key
    service_url_question = 'https://www.googleapis.com/freebase/v1/mqlread?'
    matchObj = re.match(r'(who created{0,1} +)(.+?)[?]+',query,re.I)
    if matchObj == None:
        print "The query should be \"Who created ...?\", e.g. \"Who created Microsoft?\""
        sys.exit(1)
    else:
        striped_query = matchObj.group(2).strip()
        #print striped_query
        MQL_query_author = [{'id': None, 'name': None, 'type': '/book/author',"/book/author/works_written": [{"a:name": None,"name~=": striped_query}]}]
        MQL_query_businessPerson= [{'id': None, 'name': None, 'type': '/organization/organization_founder',"/organization/organization_founder/organizations_founded": [{"a:name": None,"name~=": striped_query}]}]
        params_author = {
            "query":json.dumps(MQL_query_author),
            "key":freeBase_key,
        }
        #print freeBase_key
        #print urllib.urlencode(params_author)
        request_url_author = service_url_question+urllib.urlencode(params_author)
        response_author = json.loads(urllib.urlopen(request_url_author).read())

        #print response_author
        params_businessPerson= {
            "query":json.dumps(MQL_query_businessPerson),
            "key":freeBase_key,
        }
        #print urllib.urlencode(params)
        request_url_businessPerson= service_url_question+urllib.urlencode(params_businessPerson)
        response_businessPerson= json.loads(urllib.urlopen(request_url_businessPerson).read())

        #print response_businessPerson

        author_dic = {}
        businessPerson_dic = {}
        authbusi_list = []
        if 'error' in response_author:
            print str(response_author['error']['errors'][0]['reason'])
            sys.exit(1)
        if response_author['result']:
            for value in response_author['result']:
                if 'name' in value and '/book/author/works_written' in value:
                    author_name = str(value['name'].encode("ascii","ignore"))
                    works_list = []
                    for values in value['/book/author/works_written']:
                        if values['a:name']:
                            works_list.append(str(values['a:name'].encode("ascii","ignore")))
                if author_name not in authbusi_list:
                    authbusi_list.append(author_name)
                author_dic[author_name] = works_list
        if 'error' in response_businessPerson:
            print str(response_businessPerson['error']['errors'][0]['reason'])
            sys.exit(1)
        if response_businessPerson['result']:
            for value in response_businessPerson['result']:
                if 'name' in value and '/organization/organization_founder/organizations_founded' in value:
                    businessPerson_name = str(value['name'].encode("ascii","ignore"))
                    org_list = []
                    for values in value['/organization/organization_founder/organizations_founded']:
                        if values['a:name']:
                            org_list.append(str(values['a:name'].encode("ascii","ignore")));
                if businessPerson_name not in authbusi_list:
                    authbusi_list.append(businessPerson_name)
                businessPerson_dic[businessPerson_name] = org_list
        #print author_dic
        #print businessPerson_dic
        #sorted(author_dic.iteritems(), key=itemgetter(1))
        #sorted(businessPerson_dic.iteritems(), key=itemgetter(1))
        #print author_list
        authbusi_list.sort()
        #print author_list
        #print businessPerson_list
        print "###########################################################"
        if not author_dic and not businessPerson_dic:
            print "No results found for this query as author or business person"
            sys.exit(1)
        else:
            print 'Here are the answers to the question "Who created ' + striped_query + '?"'
            print "###########################################################"
        i=1
        for name in authbusi_list:
            #print name
            if name in author_dic:
                output_str = str(i) + '. ' + name + '(as Author) created '
                if len(author_dic[name]) == 1:
                    output_str += '<' + author_dic[name][0] +'>'
                if len(author_dic[name]) == 2:
                    output_str += '<' + author_dic[name][0] +'>'
                    output_str += " and " + '<' + author_dic[name][1] +'>'
                if len(author_dic[name]) >= 3:
                    output_str += '<' + author_dic[name][0] +'>' + ', <' + author_dic[name][1] +'>'
                    for index in range(2,len(author_dic[name])-2):
                        output_str += ", " + '<' + author_dic[name][index] +'>'
                    output_str += ", and " + '<' + author_dic[name][len(author_dic[name])-1] +'>'
                output_str += "."
                print output_str
                print "-----------------------------------------------------------"
                i+=1
            if name in businessPerson_dic:
                output_str =  str(i) + '. ' + name + '(as Businessperson) created '
                if len(businessPerson_dic[name]) == 1:
                    output_str += '<' + businessPerson_dic[name][0] +'>'
                if len(businessPerson_dic[name]) == 2:
                    output_str += '<' + businessPerson_dic[name][0] +'>'
                    output_str += " and " + businessPerson_dic[name][1] +'>'
                if len(businessPerson_dic[name]) >= 3:
                    output_str += '<' + businessPerson_dic[name][0] +'>' + ', <' +businessPerson_dic[name][1] +'>'
                    for index in range(2,len(businessPerson_dic[name])-2):
                        output_str += ", " + '<' + businessPerson_dic[name][index] +'>'
                    output_str += ", and " + '<' + businessPerson_dic[name][len(businessPerson_dic[name])-1] +'>'
                output_str += "."
                print output_str
                print "-----------------------------------------------------------"
                i+=1


def main():

        global query
        global query_type
        global freeBase_key
        global type_dict
        global info_dict

	#sys.stdout = open("transcript_"+str(uuid.uuid1())[0:6],'w')

        #parse the parameter

        my_parse = argparse.ArgumentParser(description = "Adb Proj2")
        my_parse.add_argument("-key",dest = "my_key",help='the api key for the FreeBase',type=str,default = "AIzaSyDjDDhwp3E2_Q8atQPZZ_KcAu_ZmDxyAsg")
        my_parse.add_argument("-q","--query",dest = "init_query",type=str,help='single query')
        my_parse.add_argument("-f","--file",dest = "file_path",type=str,help='batch queries file path')
        my_parse.add_argument("-t","--type",dest = "query_type",type=str,help='query type,infobox or question')


        my_para = my_parse.parse_args()
        freeBase_key = my_para.my_key
        #No Useful Option, then interactive mode
        if (not my_para.init_query) and (not my_para.file_path) and (not my_para.query_type):
            temp_input=raw_input("Entered Interactive Mode, if you don't want to continue, input q to exit and anyother input will continue the query process:\n")
            while temp_input!='q':
                my_para.query_type = raw_input("Please Input your query type: infobox | question\n")
                validateType(my_para.query_type)
                my_para.query = raw_input("Please Input your query string\n")
                if query_type == 0:
                   dict_tuple=getInfobox(my_para.query)
                   if dict_tuple:
                       displayInfobox(dict_tuple[0],dict_tuple[1])
                elif query_type == 1:
                    getQuestion(my_para.query)
                temp_input=raw_input("Entered Interactive Mode, if you don't want to continue, input q to exit and anyother input will continue the query process\n")
        elif not my_para.query_type:
            print "-t option is essential if your query option is given\n"
            sys.exit(1)
        else:
            validateType(my_para.query_type)
            query_list = []
            if my_para.file_path:
                try:
                    with open(my_para.file_path,"r") as batch_input:
                        query_list = batch_input.readlines()
                except:
                    print "File Operation Error"
            if my_para.init_query:
                query_list.append(my_para.init_query)
            #print query_list
            for index,query in enumerate(query_list):
                print "-"*100
                print "\n"
                print str(index+1) +" . The response for the query of : " + query
                print "-"*100
                print "\n"
                if query_type == 0:
                   dict_tuple=getInfobox(query)
                   if dict_tuple:
                       displayInfobox(dict_tuple[0],dict_tuple[1])
                else:
                    getQuestion(query)
                print "\n"*3
                print "-"*100



if __name__ == "__main__":
    main()
