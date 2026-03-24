const EXIT_LINKS = {
  "10bet-south-africa": "https://www.bets.co.za/link/a82c3234190213122144/",
  "apexbets": "https://record.apexaffiliates.co.za/_xfzl4TRUwAjUOsjNOfgKeWNd7ZgqdRLk/1/",
  "betbus": "https://www.bets.co.za/link/4c4b662d260118205831/",
  "betfred": "https://www.bets.co.za/link/4d0a9382190213123654/",
  "betjets": "https://www.bets.co.za/link/cb8b024250912114850/",
  "betshezi": "https://www.bets.co.za/link/9a796eb9221107160023/",
  "bettabets": "https://track.bettapartners.co.za/o/cXKljV?lpage=Fkkv_k&s1=gamingmedia",
  "betway-south-africa": "https://www.bets.co.za/link/65974d59190114175723/",
  "betxchange": "https://www.bets.co.za/link/4dbe84a5251015082400/",
  "easybet-south-africa": "https://www.bets.co.za/link/9b577ef9230623171008/",
  "gbets": "https://www.bets.co.za/link/9947adce190222182544/",
  "hollywoodbets": "https://www.bets.co.za/link/96a5aad0181116205024/",
  "jabula-bets": "https://www.bets.co.za/link/cc9032a0250318120530/",
  "jackpot-city": "https://www.bets.co.za/link/d2432c08251010140647/",
  "lucky-fish": "https://www.bets.co.za/link/5d0cc690260212095127/",
  "luckystake": "https://www.bets.co.za/link/a0fbbdac260126175628/",
  "lulabet": "https://www.bets.co.za/link/d383b695221010094649/",
  "mzansibet": "https://www.bets.co.za/link/4e6a1c8250506082921/",
  "pantherbet": "https://www.bets.co.za/link/f21fedfc250912164402/",
  "playabets": "https://www.bets.co.za/link/9cfaf6cf190222182019/",
  "playbet-co-za": "https://www.bets.co.za/link/d396cd75251113093940/",
  "pokerbet": "https://www.bets.co.za/link/2675704c230119095924/",
  "saffaluck": "https://www.bets.co.za/link/cc3c4dcd260111201048/",
  "soccershop": "https://www.bets.co.za/link/9ebdf908240402101657/",
  "sportingbet": "https://www.bets.co.za/link/24faf4f7190201004832/",
  "supabets": "https://www.bets.co.za/link/83a75fb3190222144052/",
  "supersportbet": "https://www.bets.co.za/link/ca597872250913133852/",
  "swifty": "https://www.bets.co.za/link/7f57b3bb251121120813/",
  "tictacbets": "https://www.bets.co.za/link/49302a5d260212114831/",
  "topbet": "https://www.freetips.com/link/680f3cc0190222145659/",
  "wanejo-bets": "https://www.bets.co.za/link/d7d4ec31251106143909/",
  "world-sports-betting": "https://www.bets.co.za/link/6f4efc2a190222151445/",
  "yesplay": "https://www.bets.co.za/link/22c78280220928083006/",
  "zarbet": "https://www.bets.co.za/link/53abeed4250711122151/"
};

export function onRequest(context) {
  const pathParts = context.params.path;
  const slug = (Array.isArray(pathParts) ? pathParts[0] : pathParts).replace(/\/$/, "");
  const url = EXIT_LINKS[slug];

  if (!url) {
    return new Response("Not found", { status: 404 });
  }

  return new Response(null, {
    status: 302,
    headers: {
      "Location": url,
      "Cache-Control": "no-cache, no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}
