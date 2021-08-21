$(document).ready(function () {
  $("#selectedYear").on("change", function () {
    // show the next part after selecting a year
    $("#finish-choosing").removeClass("d-none");
  });
  $("input[list]").on("click", function () {
    // zero selection when clicking on a list input
    $(this).val("");
  });



  $("table>tbody>tr>th[data-name='True'], table>tbody>tr>td[data-name='True']").each(function(){
    // for all tables - if data-name is True on a td or th - add link to player
    player = $(this).text()
    var $this = $(this)
    if (~player.indexOf('(')){
      player = $(this).text().split('(')[0]
      player = player.substring(0, player.length - 1)
    }

    $.ajax({
      url: '/get_link_from_name',
      method: 'POST',
      data:{
        player_name: player
      },
      success: function(response){
        if (response != "ERR") {
          full_link = "https://www.basketball-reference.com/players/" + response[0] + "/" + response + ".html"
          $this.find("a").attr("href", full_link)
        }
        else{
          console.log(player)
        }
      }
    })
  });

  $("#getPlayerStats").on("submit", function (e) {
    e.preventDefault();
    player_name = $("#selectedPlayer").val();
    link = $("#nbaPlayers")
      .find('option[value="' + player_name + '"]')
      .data("link");
    // start loading animation
    $("#loading").css("display", "inline-block");
    $.ajax({
      method: "POST",
      url: "/player",
      data: {
        link: link,
        year: year = $("#selectedYear").val(),
        playoffs: $("#selectPlayoffs").val()
      },
      success: function (response) {
        if (response.error == "IndexError") {
          alert("הייתה בעיה עם השנה שנבחרה, אנא בחר שנה אחרת");
        } else {
          // load all stats to screen
          $("#pos").val(response.pos);
          $("#height").val(response.height);

          $("#p3_in").val(response.p3_in);
          $("#p3_attempts").val(response.p3_attempts);
          p3_ratio = response.p3_in / response.p3_attempts;
          if (!Number.isFinite(p3_ratio)) p3_ratio = 0;
          $("#p3_ratio").html("3P% = " + p3_ratio);

          $("#p2_in").val(response.p2_in);
          $("#p2_attempts").val(response.p2_attempts);
          p2_ratio = response.p2_in / response.p2_attempts;
          if (!Number.isFinite(p2_ratio)) p2_ratio = 0;
          $("#p2_ratio").html("2P% = " + p2_ratio);

          $("#ft_in").val(response.ft_in);
          $("#ft_attempts").val(response.ft_attempts);
          ft_ratio = response.ft_in / response.ft_attempts;
          if (!Number.isFinite(ft_ratio)) ft_ratio = 0;
          $("#ft_ratio").html("FT% = " + ft_ratio);

          $("#p3_on_me").val(response.p3_on_me);
          $("#p3_attempts_on_me").val(response.p3_attempts_on_me);
          p3_ratio_on_me = response.p3_on_me / response.p3_attempts_on_me;
          if (!Number.isFinite(p3_ratio_on_me)) p3_ratio_on_me = 0;
          $("#p3_ratio_on_me").html("3PO% = " + p3_ratio_on_me);

          $("#p2_on_me").val(response.p2_on_me);
          $("#p2_attempts_on_me").val(response.p2_attempts_on_me);
          p2_ratio_on_me = response.p2_on_me / response.p2_attempts_on_me;
          if (!Number.isFinite(p2_ratio_on_me)) p2_ratio_on_me = 0;
          $("#p2_ratio_on_me").html("2PO% = " + p2_ratio_on_me);

          $("#ft_on_me").val(response.ft_on_me);
          $("#ft_attempts_on_me").val(response.ft_attempts_on_me);
          ft_ratio_on_me = response.ft_on_me / response.ft_attempts_on_me;
          if (!Number.isFinite(ft_ratio_on_me)) ft_ratio_on_me = 0;
          $("#ft_ratio_on_me").html("FTO% = " + ft_ratio_on_me);

          $("#assists").val(response.assists);
          $("#d_rebounds").val(response.d_rebounds);
          $("#off_rebound").val(response.off_rebound);
          $("#steals").val(response.steals);
          $("#blocks").val(response.blocks);
          $("#turnovers").val(response.turnovers);

          $("#p3_league_attack_from_assist_ratio").val(response.p3_league_attack_from_assist_ratio);
          $("#p2_league_attack_from_assist_ratio").val(response.p2_league_attack_from_assist_ratio);

          $("#p3_league_attack_ratio").val(response.p3_league_attack_ratio);
          $("#p2_league_attack_ratio").val(response.p2_league_attack_ratio);
          $("#ft_league_attack_ratio").val(response.ft_league_attack_ratio);
        }
        // stop loading animation
        $("#loading").css("display", "none");
        // submit form to get rating
        $("#statistics").trigger("submit");
      },
    });
  });

  $("#selectedPlayer, #selectPlayoffs").on("change", function () {
    // when changing player selection or game mode
    $("#selectYear").removeClass("d-none"); // show select year (if not displayed already)
    $("#selectedYear").val(""); // zero the year selection
    player_name = $("#selectedPlayer").val();
    player_link = "";
    $("#nbaPlayers>option").each(function () {
      if (player_name == $(this).val()) {
        player_link = $(this).data("link");
      }
    });

    $.ajax({
      type: "POST",
      url: "/get_player_years",
      data: {
        link: player_link,
        playoffs: $("#selectPlayoffs").val()
      },
      success: function (data) {
        // add years of player for a selected game mode to selection list
        $("#years").html(""); // delete other years if present
        data.forEach((element) => {
          $("#years").append("<option value=" + element + ">");
        });
      },
    });
  });

  $("#statistics").on("submit", function (e) {
    e.preventDefault();

    p3_in = parseFloat($("#p3_in").val());
    p3_attempts = parseFloat($("#p3_attempts").val());
    if (p3_attempts == 0)
      p3_ratio = 0
    else
      p3_ratio = p3_in / p3_attempts

    p2_in = parseFloat($("#p2_in").val());
    p2_attempts = parseFloat($("#p2_attempts").val());
    if (p2_attempts == 0)
      p2_ratio = 0
    else
      p2_ratio = p2_in / p2_attempts

    ft_in = parseFloat($("#ft_in").val());
    ft_attempts = parseFloat($("#ft_attempts").val());
    if (ft_attempts == 0)
      ft_ratio = 0
    else
      ft_ratio = ft_in / ft_attempts

    p3_on_me = parseFloat($("#p3_on_me").val());
    p3_attempts_on_me = parseFloat($("#p3_attempts_on_me").val());
    if (p3_attempts_on_me == 0)
      p3_attempts_on_me_ratio = 0
    else
      p3_on_me_ratio = p3_on_me / p3_attempts_on_me

    p2_on_me = parseFloat($("#p2_on_me").val());
    p2_attempts_on_me = parseFloat($("#p2_attempts_on_me").val());
    if (p2_attempts_on_me == 0)
      p2_attempts_on_me_ratio = 0
    else
      p2_on_me_ratio = p2_on_me / p2_attempts_on_me

    ft_on_me = parseFloat($("#ft_on_me").val());
    ft_attempts_on_me = parseFloat($("#ft_attempts_on_me").val());
    if (ft_attempts_on_me == 0)
      ft_attempts_on_me_ratio = 0
    else
      ft_on_me_ratio = ft_on_me / ft_attempts_on_me

    assists = parseFloat($("#assists").val());
    d_rebounds = parseFloat($("#d_rebounds").val());
    off_rebound = parseFloat($("#off_rebound").val());
    steals = parseFloat($("#steals").val());
    blocks = parseFloat($("#blocks").val());
    turnovers = parseFloat($("#turnovers").val());

    p3_league_attack_from_assist_ratio = parseFloat($("#p3_league_attack_from_assist_ratio").val());
    p2_league_attack_from_assist_ratio = parseFloat($("#p2_league_attack_from_assist_ratio").val());

    $.ajax({
      method: "POST",
      url: '/apply_formula',
      data:{
        p3_in: p3_in,
        p2_in: p2_in,
        ft_in: ft_in,
        p3_on_me: p3_on_me,
        p2_on_me: p2_on_me,
        ft_on_me: ft_on_me,
        p3_ratio: p3_ratio,
        p2_ratio: p2_ratio,
        ft_ratio: ft_ratio,
        p3_on_me_ratio: p3_on_me_ratio,
        p2_on_me_ratio: p2_on_me_ratio,
        ft_on_me_ratio: ft_on_me_ratio,
        assists: assists,
        d_rebounds: d_rebounds,
        off_rebound: off_rebound,
        steals: steals,
        blocks: blocks,
        turnovers: turnovers,
        p3_league_attack_from_assist_ratio: p3_league_attack_from_assist_ratio,
        p2_league_attack_from_assist_ratio: p2_league_attack_from_assist_ratio,
      },
      success: function(response){
        total = response.toFixed(3);
        $("#total").html("ניקוד שחקן: " + total);
        
        $(".player-total").removeClass("d-none");
        $("html, body").animate(
          {
            scrollTop: 0,
          },
          300
        );
      }
    })
  });

  $("#selectBestYear").on("click", function () {
    link = "";
    $("#nbaPlayers")
      .find("option")
      .each(function () {
        if ($(this).val() == $("#selectedPlayer").val()) {
          link = $(this).data("link");
        }
      });

    $.ajax({
      method: "POST",
      url: "/get_best_year",
      data: {
        link: link,
        playoffs: $("#selectPlayoffs").val()
      },
      success: function (response) {
        if (response != -1) { 
          $("#selectedYear").val(response);
          $("#selectedYear").trigger("change");
        }
      },
    });
  });
});
