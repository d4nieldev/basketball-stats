$(document).ready(function () {
  $("#top100>tbody>tr>th[data-name='True']").each(function(){
    original_text = $(this).text()
    var $this = $(this)

    player = $(this).text().split('(')[0]
    player = player.substring(0, player.length - 1)
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
  
  $("input[list]").on("click", function () {
    $(this).val("");
  });

  $("#getPlayerStats").on("submit", function (e) {
    e.preventDefault();
    player_name = $("#selectedPlayer").val();
    player_selector = $("#nbaPlayers")
      .find('option[value="' + player_name + '"]')
      .data("link");
    year = $("#selectedYear").val();

    $("#loading").css("display", "inline-block");
    $.ajax({
      method: "POST",
      url: "/player",
      data: {
        selector: player_selector,
        year: year,
        playoffs: $("#selectPlayoffs").val()
      },
      success: function (response) {
        if (response.error == "IndexError") {
          alert("הייתה בעיה עם השנה שנבחרה, אנא בחר שנה אחרת");
        } else {
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
        $("#loading").css("display", "none");
        $("#statistics").trigger("submit");
      },
    });
  });

  $("#selectedYear").on("change", function () {
    $("#finish-choosing").removeClass("d-none");
  });

  $("#selectedPlayer, #selectPlayoffs").on("change", function () {
    $("#selectYear").removeClass("d-none");
    $("#selectedYear").val("");
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
        console.log(data);
        $("#years").html("");
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

    p2_in = parseFloat($("#p2_in").val());
    p2_attempts = parseFloat($("#p2_attempts").val());

    ft_in = parseFloat($("#ft_in").val());
    ft_attempts = parseFloat($("#ft_attempts").val());

    p3_on_me = parseFloat($("#p3_on_me").val());
    p3_attempts_on_me = parseFloat($("#p3_attempts_on_me").val());

    p2_on_me = parseFloat($("#p2_on_me").val());
    p2_attempts_on_me = parseFloat($("#p2_attempts_on_me").val());

    ft_on_me = parseFloat($("#ft_on_me").val());
    ft_attempts_on_me = parseFloat($("#ft_attempts_on_me").val());

    assists = parseFloat($("#assists").val());
    d_rebounds = parseFloat($("#d_rebounds").val());
    off_rebound = parseFloat($("#off_rebound").val());
    steals = parseFloat($("#steals").val());
    blocks = parseFloat($("#blocks").val());
    turnovers = parseFloat($("#turnovers").val());

    p3_league_attack_from_assist_ratio = parseFloat($("#p3_league_attack_from_assist_ratio").val());
    p2_league_attack_from_assist_ratio = parseFloat($("#p2_league_attack_from_assist_ratio").val());
    ft_team_attack_ratio = parseFloat($("#ft_team_attack_ratio").val());

    $.ajax({
      method: "POST",
      url: '/apply_formula',
      data:{
        p3_in: p3_in,
        p3_attempts: p3_attempts,
        p2_in: p2_in,
        p2_attempts: p2_attempts,
        ft_in: ft_in,
        ft_attempts: ft_attempts,
        p3_on_me: p3_on_me,
        p3_attempts_on_me: p3_attempts,
        p2_on_me: p2_on_me,
        p2_attempts_on_me: p2_attempts,
        ft_on_me: ft_on_me,
        ft_attempts_on_me: ft_attempts,
        assists: assists,
        d_rebounds: d_rebounds,
        off_rebound: off_rebound,
        steals: steals,
        blocks: blocks,
        turnovers: turnovers,
        p3_league_attack_from_assist_ratio: p3_league_attack_from_assist_ratio,
        p2_league_attack_from_assist_ratio: p2_league_attack_from_assist_ratio,
        ft_team_attack_ratio: ft_team_attack_ratio,
      },
      success: function(response){
        total = response.rating
        total = total.toFixed(3);
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
        best_year = response.best_year;
        if (best_year != -1) { 
          $("#selectedYear").val(best_year);
          $("#selectedYear").trigger("change");
        }
      },
    });
  });
});
