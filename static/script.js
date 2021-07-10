$(document).ready(function () {
  $("input[list]").on("click", function () {
    $(this).val("");
  });

  $("#getPlayerStats").on("submit", function (e) {
    e.preventDefault(); 
    player_name = $("#selectedPlayer").val();
    player_selector = $("#nbaPlayers")
    .find('option[value="' + player_name + '"]')
    .data("link");
    year = $("#selectedYear").val()

    $("#loading").css("display", 'inline-block');
    $.ajax({
        method: 'POST',
        url: '/player',
        data:{
            'selector': player_selector,
            'year': year
        },
        success: function(response){
          if (response.error == "IndexError"){
            alert("הייתה בעיה עם השנה שנבחרה, אנא בחר שנה אחרת")
          }
          else{
            $("#p3_in").val(response.p3_in);
            $("#p3_attempts").val(response.p3_attempts);
            p3_ratio = response.p3_in / response.p3_attempts;
            if (!Number.isFinite(p3_ratio)) p3_ratio = 1;
            $("#p3_ratio").html(p3_ratio);

            $("#p2_in").val(response.p2_in);
            $("#p2_attempts").val(response.p2_attempts);
            p2_ratio = response.p2_in / response.p2_attempts;
            if (!Number.isFinite(p2_ratio)) p2_ratio = 1;
            $("#p2_ratio").html(p2_ratio);

            $("#ft_in").val(response.ft_in);
            $("#ft_attempts").val(response.ft_attempts);
            ft_ratio = response.ft_in / response.ft_attempts;
            if (!Number.isFinite(ft_ratio)) ft_ratio = 1;
            $("#ft_ratio").html(ft_ratio);

            $("#p3_on_me").val(response.p3_on_me);
            $("#p3_attempts_on_me").val(response.p3_attempts_on_me);
            p3_ratio_on_me = response.p3_on_me / response.p3_attempts_on_me;
            if (!Number.isFinite(p3_ratio_on_me)) p3_ratio_on_me = 1;
            $("#p3_ratio_on_me").html(p3_ratio_on_me);

            $("#p2_on_me").val(response.p2_on_me);
            $("#p2_attempts_on_me").val(response.p2_attempts_on_me);
            p2_ratio_on_me = response.p2_on_me / response.p2_attempts_on_me;
            if (!Number.isFinite(p2_ratio_on_me)) p2_ratio_on_me = 1;
            $("#p2_ratio_on_me").html(p2_ratio_on_me);

            $("#ft_on_me").val(response.ft_on_me);
            $("#ft_attempts_on_me").val(response.ft_attempts_on_me);
            ft_ratio_on_me = response.ft_on_me / response.ft_attempts_on_me;
            if (!Number.isFinite(ft_ratio_on_me)) ft_ratio_on_me = 1;
            $("#ft_ratio_on_me").html(ft_ratio_on_me);

            $("#assists").val(response.assists);
            $("#d_rebounds").val(response.d_rebounds);
            $("#off_rebound").val(response.off_rebound);
            $("#steals").val(response.steals);
            $("#blocks").val(response.blocks);
            $("#turnovers").val(response.turnovers);
            $("#minutes_of_play").val(response.minutes_of_play);

            $("#loading").css("display", 'none');
          }
        }
    })
    
  });

  $("#selectedYear").on("change", function(){
    $("#finish-choosing").removeClass('d-none');
  });

  $("#selectedPlayer").on("change", function () {
    $("#selectYear").removeClass('d-none');
    console.log("changed");
    player_name = $(this).val();
    player_link = "";
    $("#nbaPlayers>option").each(function(){
      if (player_name == $(this).val()){
        player_link = $(this).data('link');
      }
    });
    $.ajax({
      type: 'POST',
      url: '/get_player_years',
      data: {
        'link': player_link
      },
      success: function(data){
        data.forEach(element => {
          $("#years").append('<option value=' + element + '>')
        });
        
      }
    })
  });

  $("#btnNBAstats").on("click", function () {
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

  $("#statistics").on("submit", function (e) {
    e.preventDefault();

    p3_in = parseFloat($("#p3_in").val());
    p3_attempts = parseFloat($("#p3_attempts").val());
    p3_ratio = p3_in / p3_attempts;
    if (!Number.isFinite(p3_ratio)) p3_ratio = 1;
    $("#p3_ratio").html(p3_ratio);

    p2_in = parseFloat($("#p2_in").val());
    p2_attempts = parseFloat($("#p2_attempts").val());
    p2_ratio = p2_in / p2_attempts;
    if (!Number.isFinite(p2_ratio)) p2_ratio = 1;
    $("#p2_ratio").html(p2_ratio);

    ft_in = parseFloat($("#ft_in").val());
    ft_attempts = parseFloat($("#ft_attempts").val());
    ft_ratio = ft_in / ft_attempts;
    if (!Number.isFinite(ft_ratio)) ft_ratio = 1;
    $("#ft_ratio").html(ft_ratio);

    p3_on_me = parseFloat($("#p3_on_me").val());
    p3_attempts_on_me = parseFloat($("#p3_attempts_on_me").val());
    p3_ratio_on_me = p3_on_me / p3_attempts_on_me;
    if (!Number.isFinite(p3_ratio_on_me)) p3_ratio_on_me = 1;
    $("#p3_ratio_on_me").html(p3_ratio_on_me);

    p2_on_me = parseFloat($("#p2_on_me").val());
    p2_attempts_on_me = parseFloat($("#p2_attempts_on_me").val());
    p2_ratio_on_me = p2_on_me / p2_attempts_on_me;
    if (!Number.isFinite(p2_ratio_on_me)) p2_ratio_on_me = 1;
    $("#p2_ratio_on_me").html(p2_ratio_on_me);

    ft_on_me = parseFloat($("#ft_on_me").val());
    ft_attempts_on_me = parseFloat($("#ft_attempts_on_me").val());
    ft_ratio_on_me = ft_on_me / ft_attempts_on_me;
    if (!Number.isFinite(ft_ratio_on_me)) ft_ratio_on_me = 1;
    $("#ft_ratio_on_me").html(ft_ratio_on_me);

    assists = parseFloat($("#assists").val());
    d_rebounds = parseFloat($("#d_rebounds").val());
    off_rebound = parseFloat($("#off_rebound").val());
    steals = parseFloat($("#steals").val());
    blocks = parseFloat($("#blocks").val());
    turnovers = parseFloat($("#turnovers").val());
    minutes_of_play = parseFloat($("#minutes_of_play").val());

    p3_team_ratio = parseFloat($("#p3_team_ratio").val());
    p2_team_ratio = parseFloat($("#p2_team_ratio").val());
    ft_team_ratio = parseFloat($("#ft_team_ratio").val());

    p3_team_attack_ratio = parseFloat($("#p3_team_attack_ratio").val());
    p2_team_attack_ratio = parseFloat($("#p2_team_attack_ratio").val());
    ft_team_attack_ratio = parseFloat($("#ft_team_attack_ratio").val());

    p3_league_ratio = parseFloat($("#p3_league_ratio").val());
    p2_league_ratio = parseFloat($("#p2_league_ratio").val());
    ft_league_ratio = parseFloat($("#ft_league_ratio").val());

    p3_league_attack_ratio = parseFloat($("#p3_league_attack_ratio").val());
    p2_league_attack_ratio = parseFloat($("#p2_league_attack_ratio").val());
    ft_league_attack_ratio = parseFloat($("#ft_league_attack_ratio").val());

    assist_val =
      3 * p3_league_attack_ratio +
      2 * p2_league_attack_ratio -
      (3 * p3_team_ratio * p3_team_attack_ratio +
        2 * p2_team_attack_ratio * p2_team_ratio);
    d_rebound_val =
      3 * p3_league_attack_ratio * p3_league_ratio +
      2 * p2_league_attack_ratio * p2_league_ratio +
      2 * ft_league_ratio * ft_league_attack_ratio;
    off_rebound_val =
      d_rebound_val +
      2 * p2_ratio * p2_league_attack_ratio +
      2 * ft_ratio * ft_league_attack_ratio;
    steal_val =
      d_rebound_val +
      3 * p3_ratio * p3_league_attack_ratio +
      2 * p2_ratio * p2_league_attack_ratio +
      2 * ft_ratio * ft_league_attack_ratio;
    block_val = 0.57 * d_rebound_val;
    turnover_val = d_rebound_val +
    3 * p3_league_ratio * p3_league_attack_ratio +
    2 * p2_league_ratio * p2_league_attack_ratio +
    2 * ft_league_ratio * ft_league_attack_ratio;

    total =
      3 * p3_in * p3_ratio +
      2 * p2_in * p2_ratio +
      1 * ft_in * ft_ratio +
      assist_val * assists +
      d_rebound_val * d_rebounds +
      off_rebound_val * off_rebound +
      steal_val * steals +
      block_val * blocks -
      turnover_val * turnovers -
      (3 * p3_on_me * p3_ratio_on_me +
        2 * p2_on_me * p2_ratio_on_me +
        1 * ft_on_me * ft_ratio_on_me);
    total /= minutes_of_play;

    $("#total").html("ניקוד שחקן: " + total);
    $(".player-total").removeClass('d-none');
    $("html, body").animate({
        scrollTop: 0
    }, 300);   
  });
});
