$(document).ready(function(){
    $("#sendToStatistics").on("click", function(){
        player_name = $("#selectedOption").val()
        player_selector = $("#nbaPlayers").find("option[value='" + player_name + "']").data('link')
        window.open('/player/' + player_selector);
    });

    $("#btnNBAstats").on("click", function(){
        console.log("!");
        $("#p3_team_ratio").val("0.38");
        $("#p2_team_ratio").val("0.48");
        $("#ft_team_ratio").val("0.8");
        $("#p3_team_attack_ratio").val("0.24");
        $("#p2_team_attack_ratio").val("0.6");
        $("#ft_team_attack_ratio").val("0.16");

        $("#p3_league_ratio").val("0.38");
        $("#p2_league_ratio").val("0.48");
        $("#ft_league_ratio").val("0.8");
        $("#p3_league_attack_ratio").val("0.24");
        $("#p2_league_attack_ratio").val("0.6");
        $("#ft_league_attack_ratio").val("0.16");
    });

    $("#statistics").on("submit", function(e){
        e.preventDefault();

        p3_in = parseFloat($("#p3_in").val())
        p3_attempts = parseFloat($("#p3_attempts").val())
        p3_ratio = p3_in / p3_attempts
        if (!Number.isFinite(p3_ratio)) p3_ratio = 1
        $("#p3_ratio").html(p3_ratio)

        p2_in = parseFloat($("#p2_in").val())
        p2_attempts = parseFloat($("#p2_attempts").val())
        p2_ratio = p2_in / p2_attempts
        if (!Number.isFinite(p2_ratio)) p2_ratio = 1
        $("#p2_ratio").html(p2_ratio)

        ft_in = parseFloat($("#ft_in").val())
        ft_attempts = parseFloat($("#ft_attempts").val())
        ft_ratio = ft_in / ft_attempts
        if (!Number.isFinite(ft_ratio)) ft_ratio = 1
        $("#ft_ratio").html(ft_ratio)

        p3_on_me = parseFloat($("#p3_on_me").val())
        p3_attempts_on_me = parseFloat($("#p3_attempts_on_me").val())
        p3_ratio_on_me = p3_on_me / p3_attempts_on_me
        if (!Number.isFinite(p3_ratio_on_me)) p3_ratio_on_me = 1
        $("#p3_ratio_on_me").html(p3_ratio_on_me)

        p2_on_me = parseFloat($("#p2_on_me").val())
        p2_attempts_on_me = parseFloat($("#p2_attempts_on_me").val())
        p2_ratio_on_me = p2_on_me / p2_attempts_on_me
        if (!Number.isFinite(p2_ratio_on_me)) p2_ratio_on_me = 1
        $("#p2_ratio_on_me").html(p2_ratio_on_me)

        ft_on_me = parseFloat($("#ft_on_me").val())
        ft_attempts_on_me = parseFloat($("#ft_attempts_on_me").val())
        ft_ratio_on_me = ft_on_me / ft_attempts_on_me
        if (!Number.isFinite(ft_ratio_on_me)) ft_ratio_on_me = 1
        $("#ft_ratio_on_me").html(ft_ratio_on_me)

        assists = parseFloat($("#assists").val())
        d_rebounds = parseFloat($("#d_rebounds").val())
        off_rebound = parseFloat($("#off_rebound").val())
        steals = parseFloat($("#steals").val())
        blocks = parseFloat($("#blocks").val())
        turnovers = parseFloat($("#turnovers").val())
        minutes_of_play = parseFloat($("#minutes_of_play").val())

        p3_team_ratio = parseFloat($("#p3_team_ratio").val())
        p2_team_ratio = parseFloat($("#p2_team_ratio").val())
        ft_team_ratio = parseFloat($("#ft_team_ratio").val())

        p3_team_attack_ratio = parseFloat($("#p3_team_attack_ratio").val())
        p2_team_attack_ratio = parseFloat($("#p2_team_attack_ratio").val())
        ft_team_attack_ratio = parseFloat($("#ft_team_attack_ratio").val())

        p3_league_ratio = parseFloat($("#p3_league_ratio").val())
        p2_league_ratio = parseFloat($("#p2_league_ratio").val())
        ft_league_ratio = parseFloat($("#ft_league_ratio").val())

        p3_league_attack_ratio = parseFloat($("#p3_league_attack_ratio").val())
        p2_league_attack_ratio = parseFloat($("#p2_league_attack_ratio").val())
        ft_league_attack_ratio = parseFloat($("#ft_league_attack_ratio").val())

        

        assist_val = 3*p3_league_attack_ratio + 2*p2_league_attack_ratio + 2*ft_league_attack_ratio*ft_league_ratio - (3*p3_team_ratio*p3_team_attack_ratio + 2*p2_team_attack_ratio*p2_team_ratio + 2*ft_team_ratio*ft_team_attack_ratio)
        d_rebound_val = 3*p3_league_attack_ratio*p3_league_ratio + 2*p2_league_attack_ratio*p2_league_ratio + 2*ft_league_ratio*ft_league_attack_ratio
        off_rebound_val = d_rebound_val + 2*p2_ratio*p2_league_attack_ratio + 2*ft_ratio*ft_league_attack_ratio
        steal_val = d_rebound_val + 3*p3_ratio*p3_league_attack_ratio + 2*p2_ratio*p2_league_attack_ratio + 2*ft_ratio*ft_league_attack_ratio
        block_val = 0.57*d_rebound_val
        turnover_val = steal_val

        total = p3_in*p3_ratio + p2_in*p2_ratio + ft_in*ft_ratio + assist_val*assists + d_rebound_val*d_rebounds + off_rebound_val*off_rebound + steal_val*steals + block_val*blocks - turnover_val*turnovers - (p3_on_me*p3_ratio_on_me + p2_on_me*p2_ratio_on_me + ft_on_me*ft_ratio_on_me)
        total = total / minutes_of_play

        $("#total").html("ניקוד שחקן: " + total)
    });
});