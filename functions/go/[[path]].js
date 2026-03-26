const EXIT_LINKS = {
  "10bet-south-africa": "https://www.mzansiwins.co.za/link/a82c3234190213122144/146/",
  "apexbets": "https://www.mzansiwins.co.za/link/754825e7260306164405/146/",
  "betbus": "https://www.mzansiwins.co.za/link/fd10f517260118211403/146/",
  "betfred": "https://www.mzansiwins.co.za/link/4d0a9382190213123654/146/",
  "betjets": "https://www.mzansiwins.co.za/link/cb8b024250912114850/146/",
  "betshezi": "https://www.mzansiwins.co.za/link/9a796eb9221107160023/146/",
  "bettabets": "https://www.mzansiwins.co.za/link/56eef481260312134641/146/",
  "betway-south-africa": "https://www.mzansiwins.co.za/link/65974d59190114175723/146/",
  "betxchange": "https://www.mzansiwins.co.za/link/f1600f69251013161439/146/",
  "easybet-south-africa": "https://www.mzansiwins.co.za/link/9b577ef9230623171008/146/",
  "gbets": "https://www.mzansiwins.co.za/link/9947adce190222182544/146/",
  "hollywoodbets": "https://www.mzansiwins.co.za/link/96a5aad0181116205024/146/",
  "jabula-bets": "https://www.mzansiwins.co.za/link/cc9032a0250318120530/146/",
  "jackpot-city": "https://www.mzansiwins.co.za/link/d2432c08251010140647/146/",
  "lucky-fish": "https://www.mzansiwins.co.za/link/5d0cc690260212095127/146/",
  "luckystake": "https://www.mzansiwins.co.za/link/a0fbbdac260126175628/146/",
  "lulabet": "https://www.mzansiwins.co.za/link/d383b695221010094649/146/",
  "mzansibet": "https://www.mzansiwins.co.za/link/4e6a1c8250506082921/146/",
  "pantherbet": "https://www.mzansiwins.co.za/link/f21fedfc250912164402/146/",
  "playabets": "https://www.mzansiwins.co.za/link/9cfaf6cf190222182019/146/",
  "playbet-co-za": "https://www.mzansiwins.co.za/link/d396cd75251113093940/146/",
  "pokerbet": "https://www.mzansiwins.co.za/link/2675704c230119095924/146/",
  "saffaluck": "https://www.mzansiwins.co.za/link/ea4ccdb3260111202147/146/",
  "soccershop": "https://www.mzansiwins.co.za/link/9ebdf908240402101657/146/",
  "sportingbet": "https://www.mzansiwins.co.za/link/53d0c234190213110607/146/",
  "supabets": "https://www.mzansiwins.co.za/link/83a75fb3190222144052/146/",
  "supersportbet": "https://www.mzansiwins.co.za/link/ca597872250913133852/146/",
  "swifty": "https://www.mzansiwins.co.za/link/7f57b3bb251121120813/146/",
  "tictacbets": "https://www.mzansiwins.co.za/link/49302a5d260212114831/146/",
  "topbet": "https://www.mzansiwins.co.za/link/680f3cc0190222145659/146/",
  "wanejo-bets": "https://www.mzansiwins.co.za/link/d7d4ec31251106143909/146/",
  "world-sports-betting": "https://www.mzansiwins.co.za/link/6f4efc2a190222151445/146/",
  "yesplay": "https://www.mzansiwins.co.za/link/22c78280220928083006/146/",
  "zarbet": "https://www.mzansiwins.co.za/link/53abeed4250711122151/146/"
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
