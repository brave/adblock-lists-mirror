// ==UserScript==
// @name            Bypass Paywalls Clean - nl/be
// @version         4.2.2.5
// @description     Bypass Paywalls of news sites
// @author          magnolia1234
// @downloadURL     https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.nl.user.js
// @updateURL       https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc.nl.user.js
// @homepageURL     https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters
// @supportURL      https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters
// @license         MIT; https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=LICENSE
// @noframes
// @match           *://*.nl/*
// @match           *://*.businessam.be/*
// @match           *://*.demorgen.be/*
// @match           *://*.doorbraak.be/*
// @match           *://*.flair.be/nl/*
// @match           *://*.gva.be/*
// @match           *://*.hbvl.be/*
// @match           *://*.hln.be/*
// @match           *://*.humo.be/*
// @match           *://*.knack.be/*
// @match           *://*.kw.be/*
// @match           *://*.libelle.be/*
// @match           *://*.nieuwsblad.be/*
// @match           *://*.projectcargojournal.com/*
// @match           *://*.railfreight.cn/*
// @match           *://*.railfreight.com/*
// @match           *://*.railtech.be/*
// @match           *://*.railtech.com/*
// @match           *://*.standaard.be/*
// @match           *://*.taxipro.be/*
// @match           *://*.tijd.be/*
// @connect         archive.fo
// @connect         archive.is
// @connect         archive.li
// @connect         archive.md
// @connect         archive.ph
// @connect         archive.vn
// @grant           GM.xmlHttpRequest
// @require         https://gitflic.ru/project/magnolia1234/bypass-paywalls-clean-filters/blob/raw?file=userscript/bpc_func.js
// ==/UserScript==

(function() {
  //'use strict';

window.setTimeout(function () {

var be_mediahuis_domains = ['gva.be', 'hbvl.be', 'nieuwsblad.be', 'standaard.be'];
var be_roularta_domains = ['beleggersbelangen.nl', 'flair.be', 'knack.be', 'kw.be', 'libelle.be'];
var nl_dpg_adr_domains = ['ad.nl', 'bd.nl', 'bndestem.nl', 'destentor.nl', 'ed.nl', 'gelderlander.nl', 'pzc.nl', 'tubantia.nl'];
var nl_dpg_media_domains = ['demorgen.be', 'flair.nl', 'humo.be', 'libelle.nl', 'margriet.nl', 'parool.nl', 'trouw.nl', 'volkskrant.nl'];
var nl_mediahuis_region_domains = ['gooieneemlander.nl', 'haarlemsdagblad.nl', 'ijmuidercourant.nl', 'leidschdagblad.nl', 'limburger.nl', 'noordhollandsdagblad.nl'];

if (matchDomain('adformatie.nl')) {
  document.querySelectorAll('iframe[uc-src]').forEach(e => e.src = e.getAttribute('uc-src'));
  let ads = 'div.c-ad-slot';
  hideDOMStyle(ads);
}

else if (matchDomain(be_mediahuis_domains)) {
  window.setTimeout(function () {
    let video = document.querySelector('div.video, div[data-testid="article-video"]');
    func_post = function () {
      let article = document.querySelector(article_sel);
      if (article) {
        if (video) {
          if (matchDomain(['gva.be', 'nieuwsblad.be'])) {
            let placeholder = video.querySelector('div[class^="Placeholder_placeholder"]');
            if (placeholder)
              placeholder.removeAttribute('class');
          }
          let video_new = article.querySelector('div[id$="-streamone"], div[id^="video-player-"], div[id^="player_"]');
          if (video_new && video_new.parentNode)
            video_new.parentNode.replaceChild(video, video_new);
          else {
            let header = article.querySelector('h1');
            let br = document.createElement('br');
            if (header)
              header.after(br, video, br);
          }
        }
        let errors = document.querySelectorAll('div[height][old-src]:not([src]):has(div#__next_error__)');
        for (let elem of errors) {
          let iframe = document.createElement('iframe');
          iframe.src = elem.getAttribute('old-src');
          iframe.style = 'width: 100%; height: ' + elem.getAttribute('height') + 'px;';
          elem.parentNode.replaceChild(iframe, elem);
        }
        if (mobile) {
          if (article_main) {
            let div_next = document.querySelector('div[id="__next"]');
            if (div_next)
              article.style.width = div_next.offsetWidth + 'px';
          }
          let lazy_images = article.querySelectorAll('figure img[loading="lazy"][style]');
          for (let elem of lazy_images)
            elem.style = 'width: 95%;';
          let figures = article.querySelectorAll('figure div');
          for (let elem of figures) {
            elem.removeAttribute('style');
            let svg = elem.querySelector('svg');
            removeDOMElement(svg);
          }
        }
        let pars = article.querySelectorAll('div[style*="font-size"]');
        if (pars.length < 5)
          article.before(googleSearchToolLink(url));
      }
    }
    let url = window.location.href;
    let paywall_sel = 'head > meta[name$="article_ispaidcontent"][content="true"]';
    let article_sel = 'main > article';
    let article_main = document.querySelector(article_sel);
    if (!article_main)
      article_sel = 'article[role="article"] div[id]';
    getArchive(url, paywall_sel, '', article_sel);
    let popup = document.querySelector('div[data-testid="close-popup-button"]');
    if (popup)
      popup.click();
  }, 1500);
  let ads = 'div[id^="ad_inline-"]';
  hideDOMStyle(ads);
}

else if (matchDomain('businessam.be')) {
  let paywall = document.querySelector('div.paywall');
  if (paywall) {
    removeDOMElement(paywall);
    let article = document.querySelector('div.text-gradient');
    if (article) {
      let scripts = document.querySelectorAll('script:not([src]):not([type])');
      let content_script;
      for (let script of scripts) {
        if (script.text.match(/window\.fullcontent64\s?=\s?"/)) {
          content_script = script;
          break;
        }
      }
      if (content_script) {
        try {
          let content = decode_utf8(atob(content_script.text.split(/window\.fullcontent64\s?=\s?"/)[1].split('";')[0]));
          let parser = new DOMParser();
          let doc = parser.parseFromString('<div>' + content + '</div>', 'text/html');
          let content_new = doc.querySelector('div');
          article.parentNode.replaceChild(content_new, article);
        } catch (err) {
          console.log(err);
        }
      }
    }
  }
}

else if (matchDomain('businessinsider.nl')) {
  getJsonUrl('div.piano-article__paywall', '', 'div.piano-article__content');
}

else if (matchDomain('doorbraak.be')) {
  window.setTimeout(function () {
    let plus = document.querySelector('h1 > svg');
    let article = document.querySelector('div > div.prose');
    if (plus && article) {
      let paywall_sel = 'div.paywall';
      let paywall = document.querySelector(paywall_sel);
      let pars = article.querySelectorAll('p');
      if (paywall || pars.length < 2) {
        removeDOMElement(paywall);
        waitDOMElement(paywall_sel, 'DIV', removeDOMElement, false);
        let json_script = document.querySelector('script#__NUXT_DATA__');
        if (json_script) {
          try {
            if (!json_script.text.substr(0, 500).includes(window.location.pathname))
              refreshCurrentTab();
            let json = JSON.parse(json_script.text);
            json = json.filter(x => typeof x === 'string' && x.startsWith('<p>'));
            let json_text = json[0];
            if (json_text) {
              let parser = new DOMParser();
              let doc = parser.parseFromString('<div>' + json_text + '</div>', 'text/html');
              let content_new = doc.querySelector('div');
              article.appendChild(content_new);
            }
          } catch (err) {
            console.log(err);
          }
        }
      }
    }
  }, 1000);
}

else if (matchDomain(be_roularta_domains)) {
  if (matchDomain('beleggersbelangen.nl')) {
    let paywall = document.querySelector('div.unlimited-access');
    if (paywall) {
      removeDOMElement(paywall);
      let no_account = document.querySelector('div.no-account');
      if (no_account)
        no_account.classList.remove('no-account');
      let content_inner = document.querySelector('div.content-inner[style]');
      if (content_inner)
        content_inner.removeAttribute('style');
    }
  } else {
    let paywall = document.querySelector('div[id*="wall-modal"]');
    if (paywall) {
      removeDOMElement(paywall);
      let html = document.querySelector('html[class]');
      if (html)
        html.removeAttribute('class');
      function roularta_noscroll(node) {
        node.removeAttribute('style');
        node.removeAttribute('class');
      }
      waitDOMAttribute('html', 'html', 'class', roularta_noscroll, true);
      let intro = document.querySelectorAll('div.article-body > p, div.article-body > style');
      removeDOMElement(...intro);
      let locked = document.querySelector('body.locked');
      if (locked)
        locked.classList.remove('locked');
    }
    if (!window.navigator.userAgent.toLowerCase().includes('chrome') && !matchDomain(['kw.be']) && window.location.href.match(/\/(\w+-){2,}/)) {
      let lazy_images = document.querySelectorAll('img[src^="data:image/"][data-lazy-src]');
      for (let elem of lazy_images) {
        elem.src = elem.getAttribute('data-lazy-src');
      }
    }
  }
  let ads = 'div.rmgAd, div.c-header__ad';
  hideDOMStyle(ads);
}

else if (matchDomain('ftm.nl')) {
  let videos = document.querySelectorAll('div.body > div.video-pp');
  for (let video of videos) {
    let video_id_dom = video.querySelector('a.video[data-youtube-id]');
    if (video_id_dom) {
      video_new = document.createElement('iframe');
      video_new.src = 'https://www.youtube.com/embed/' + video_id_dom.getAttribute('data-youtube-id');
      video_new.style = 'width: 95%; height: 400px; margin: 0px 20px;';
      video.parentNode.replaceChild(video_new, video);
    }
  }
  let audio_controls = document.querySelectorAll('audio[controls][style]');
  for (let elem of audio_controls)
    elem.removeAttribute('style');
  document.querySelectorAll('div.foldable').forEach(e => e.classList.remove('foldable'));
  let banners = 'div.banner-pp';
  hideDOMStyle(banners);
}

else if (matchDomain('groene.nl')) {
  let url = window.location.href;
  getArchive(url, 'div#closed-block', '', 'article');
  let more = pageContains('div.wrapper > h2', 'Verder lezen?');
  if (more.length) {
    let link_text = 'https://www.groene.nl/populair';
    let a_link = document.createElement('a');
    a_link.href = link_text;
    a_link.innerText = 'BPC > ' + link_text.split('www.')[1];
    more[0].parentNode.append(document.createElement('br'), a_link);
  }
}

else if (matchDomain(['lc.nl', 'dvhn.nl']) || document.querySelector('head > link[href*=".ndcmediagroep.nl/"]')) {
  let paywall = document.querySelector('div.signupPlus, div.pw-wrapper');
  if (paywall) {
    let intro = document.querySelector('div.startPayWall');
    let html = document.documentElement.outerHTML;
    if (html.includes('window.__NUXT__=')) {
      removeDOMElement(paywall, intro);
      try {
        let json = html.split('window.__NUXT__=')[1].split('</script>')[0].trim();
        let json_match = json.includes('type:"article",');
        if (json_match) {
          let path_match = window.location.pathname.match(/-(\d+)\./);
          if (path_match) {
            let article_id = path_match[1];
            json_match = json.includes(',id:"' + article_id + '",');
            if (!json_match && json.match(/[(,]null,/)) {
              let art_match = json.split(/[(,]null,/)[1].match(new RegExp('-' + article_id + '\\.', 'g'));
              json_match = art_match && art_match.length > 1;
            }
          }
        }
        if (!json_match)
          refreshCurrentTab();
        else if (json.includes(',body:')) {
          let nuxt_vars = json.split(/^\(function\(/)[1].split('){')[0].split(',');
          let nuxt_values = json.split('}}(')[1].split('));')[0].replace(/,(true|false|\d+|{}),/g, ',"$1",').replace(/,(null),/g, ',"$1",').replace(/,(void\s\d),/g, ',"$1",').split(/\\?",\\?"/);
          function findNuxtText(str, attributes = false) {
            if (nuxt_vars.length && nuxt_values.length && !(attributes && str.length === 1 && str === str.toUpperCase())) {
              let index = nuxt_vars.indexOf(str);
              if (nuxt_values[index])
                str = nuxt_values[index];
            }
            return str;
          }
          let intro;
          let intro_match = json.match(/,leadtext_raw:"([^"]+)",/);
          let intro_meta_dom = document.querySelector('head > meta[data-hid="description"][content]');
          if (intro_match || intro_meta_dom) {
            intro = document.createElement('p');
            intro.innerText = intro_match ? intro_match[1].replace(/\\u002F/g, '/') : intro_meta_dom.content;
            intro.style = 'font-weight: bold;';
          }
          let json_text = json.split(',body:')[1].split(/,(leadText|brand_key|tts|pianoKeywords):/)[0].replace(/([{,])(\w+)(?=:(["\{\[]|[\w$]{1,2}[,\}]))/g, "$1\"$2\"").replace(/(Image\\":)(\d)([,}])/g, '$1\\"$2\\"$3').replace(/\":(\[)?([\w\$\.]+)([\]},])/g, "\":$1\"$2\"$3");
          let article = document.querySelector('div.content');
          if (article) {
            article.innerHTML = '';
            if (intro)
              article.appendChild(intro);
            let pars = JSON.parse(json_text);
            function addParText(elem, par_text, add_br = false, attributes = false) {
              if (par_text) {
                if (par_text.length <= 2)
                  par_text = findNuxtText(par_text, attributes);
                let span = document.createElement('span');
                span.innerText = par_text;
                elem.appendChild(span);
                if (add_br)
                  elem.appendChild(document.createElement('br'));
              }
            }
            function addLink(elem, link_text, href, add_br = false) {
              let par_link = document.createElement('a');
              par_link.href = href;
              par_link.innerText = link_text;
              elem.appendChild(par_link);
              if (add_br)
                elem.appendChild(document.createElement('br'));
            }
            function addImage(elem, child) {
              let figure = document.createElement('figure');
              let img = document.createElement('img');
              img.src = child.relation.href;
              figure.appendChild(img);
              if (child.relation.caption) {
                if (child.relation.caption.length <= 2)
                  child.relation.caption = findNuxtText(child.relation.caption).replace(/\\"/g, '"').replace(/\\n/g, ' - ').replace(/\\u002F/g, '/');
                if (child.relation.photographer) {
                  if (child.relation.photographer.length <= 2)
                    child.relation.photographer = findNuxtText(child.relation.photographer).replace(/\\u002F/g, '/');
                  child.relation.caption += ' - ' + child.relation.photographer;
                }
                let caption = document.createElement('figcaption');
                caption.innerText = child.relation.caption;
                figure.appendChild(caption);
              }
              elem.appendChild(figure);
            }
            function addChildren(elem, children, add_br = false, attributes = false) {
              for (let child of children) {
                if (child.text) {
                  addParText(elem, child.text, add_br, attributes);
                } else if (child.relation && (child.type === 'img' || child.relation.caption) && child.relation.href) {
                  let img_par = document.createElement('p');
                  addImage(img_par, child);
                  elem.appendChild(img_par);
                } else if (child.relation && child.relation.link) {
                  if (child.relation.link.length <= 2)
                    child.relation.link = findNuxtText(child.relation.link).replace(/\\u002F/g, '/');
                  if (child.relation.title.length <= 2)
                    child.relation.title = findNuxtText(child.relation.title);
                  addLink(elem, child.relation.title, child.relation.link);
                } else if (child.children) {
                  if (child.children.length) {
                    for (let item of child.children) {
                      if (item.text) {
                        if ((child.href && child.href.length > 2) || (child.relation && child.relation.follow && child.relation.follow.url)) {
                          if (item.text.length > 2)
                            addLink(elem, item.text, child.href || child.relation.follow.url, add_br);
                        } else
                          addParText(elem, item.text, false, child.attributes && child.attributes.length);
                      } else
                        addChildren(elem, item.children, false, item.attributes && item.attributes.length);
                    }
                  } else
                    elem.appendChild(document.createElement('br'));
                }
              }
            }
            for (let par of pars) {
              let elem = document.createElement('p');
              if (par.code) {
                let parser = new DOMParser();
                let doc = parser.parseFromString('<div>' + par.code + '</div>', 'text/html');
                elem = doc.querySelector('div');
              } else if (par.insertbox_head || par.insertbox_text) {
                if (par.insertbox_head && par.insertbox_head.length > 2)
                  addParText(elem, par.insertbox_head, true);
                if (par.insertbox_text) {
                  for (let item of par.insertbox_text) {
                    if (item.children)
                      addChildren(elem, item.children, true);
                  }
                }
              } else if (par.text) {
                if (findNuxtText(par.type) !== 'streamer')
                  addParText(elem, par.text);
              } else if (par.children) {
                addChildren(elem, par.children);
              } else if (par.typename.length > 2)
                console.log(par);
              if (elem.hasChildNodes()) {
                article.appendChild(elem);
              }
            }
          }
        }
      } catch (err) {
        console.log(err);
      }
    }
  }
  let ads = 'div.top__ad, div.marketingblock-article';
  hideDOMStyle(ads);
}

else if (matchDomain('linda.nl')) {
  window.setTimeout(function () {
    let paywall = document.querySelector('div.premium-login-box_loginBox');
    if (paywall) {
      removeDOMElement(paywall);
      let article = document.querySelector('div[class*="_loginRequired"]');
      if (article) {
        let filter = /^window\.__INITIAL_PROPS__\s?=\s?/;
        let json_script = getSourceJsonScript(filter);
        if (json_script) {
          try {
            let json = JSON.parse(json_script.text.split(filter)[1]);
            if (json) {
              let slug = json.slug;
              if ((slug && !window.location.pathname.includes(slug)) || !json.viewData)
                refreshCurrentTab();
              if (json && json.viewData.article) {
                function replace_also_read(str) {
                  return str.replace(/{also-read title="([^}]+)" url="([^}]+)" [^}]+"}/g, "<div style='margin: 15px 0px'><a href=\"$2\">Lees ook: $1</a></div>");
                }
                article.className = article.className.replace(/[-\w]+_loginRequired/, '');
                if (json.viewData.article.modules) {
                  let modules = json.viewData.article.modules;
                  article.innerHTML = '';
                  for (let elem of modules) {
                    let type = elem.acf_fc_layout;
                    if (type) {
                      let item = document.createElement('div');
                      if (['body_text', 'intro', 'quote'].includes(type)) {
                        if (elem.text) {
                          let parser = new DOMParser();
                          let doc = parser.parseFromString('<div style="margin: 20px;">' + replace_also_read((elem.title ? elem.title : '') + elem.text.replace(/\r\n/g, '<br>')) + '</div>', 'text/html');
                          item = doc.querySelector('div');
                          if (type === 'intro') {
                            let intro = item.querySelector('p');
                            if (intro)
                              intro.style = 'font-weight: bold; ';
                          } else if (type === 'quote')
                            item.style['text-align'] = 'center';
                          article.append(item);
                        }
                      } else if (type === 'image') {
                        let elem_images = elem.images_portrait || elem.images_landscape;
                        if (elem_images && elem_images.length) {
                          for (let img of elem_images) {
                            let url = img.image.sizes.large;
                            let caption_text = img.credits ? img.credits.replace(/(\n|<[^<]*>)/g, '') : '';
                            item = makeFigure(url, caption_text, {style: 'width: 100%;'});
                            article.append(item);
                          }
                        }
                      } else
                        console.log(elem);
                    }
                  }
                } else if (json.viewData.article.body) {
                  let parser = new DOMParser();
                  let doc = parser.parseFromString('<div>' + replace_also_read(json.viewData.article.body) + '</div>', 'text/html');
                  let article_new = doc.querySelector('div');
                  if (article_new) {
                    article.innerHTML = '';
                    article.appendChild(article_new);
                  }
                } else
                  header_nofix('div.article-content_base');
              }
            }
          } catch (err) {
            console.log(err);
          }
        }
      }
    }
  }, 1000);
}

else if (matchDomain(nl_dpg_adr_domains.concat(['hln.be']))) {
  func_post = function () {
    let article = document.querySelector(article_sel);
    if (article) {
      let shades = article.querySelectorAll('div[style*="background-color"][style*=";width"]');
      for (let elem of shades)
        elem.style.width = '85%';
      let lazy_images = article.querySelectorAll('picture img[loading="lazy"][style]');
      for (let elem of lazy_images)
        elem.style = 'width: 95%;';
      let widgets = article.querySelectorAll('div > div > div[old-src]:not([src])');
      for (let elem of widgets) {
        let iframe = document.createElement('iframe');
        iframe.src = elem.getAttribute('old-src');
        iframe.style = 'width: 100%; border: none;';
        if (iframe.src.includes('/widgets/') || iframe.src.includes('/playlists/'))
          iframe.style.height = '400px';
        elem.parentNode.replaceChild(iframe, elem);
      }
      let errors = article.querySelectorAll('div > div[old-src]:not([src]):has(div#main-frame-error)');
      for (let elem of errors) {
        let elem_new = document.createElement('iframe');
        elem_new.src = elem.getAttribute('old-src');
        elem_new.style = 'width: 100%; height: 400px; border: none;';
        elem.parentNode.removeAttribute('style');
        elem.parentNode.replaceChild(elem_new, elem);
      }
      let picture_divs = article.querySelectorAll('picture > div[style*="min-height:"]:has(svg)');
      for (let elem of picture_divs) {
        elem.parentNode.removeAttribute('style');
        removeDOMElement(elem);
      }
      let video_scripts = article.querySelectorAll('div > div > script[type="application/ld+json"], article > script[type="application/ld+json"]');
      for (let elem of video_scripts) {
        if (elem.text.includes(',"embedUrl":"')) {
          let iframe = document.createElement('iframe');
          iframe.src = elem.text.split(',"embedUrl":"')[1].split('"')[0];
          iframe.style = 'width: 100%; height: 400px;';
          let container = elem.parentNode;
          if (elem.parentNode.tagName === 'DIV')
            container = container.parentNode;
          container.parentNode.replaceChild(iframe, container);
        }
      }
    }
    if (matchDomain('hln.be')) {
      let article_divs = document.querySelectorAll(article_src_sel + ' > div');
      if (article_divs.length < 3)
        header_nofix(article_sel + ' > header', '', 'BPC > no archive-fix');
    } else
      header_nofix(article_sel + ' > header', 'article[id^="PURCHASE"]', 'BPC > no archive-fix');
  }
  let url = window.location.href;
  let article_sel = 'div#remaining-paid-content';
  let article_src_sel = 'div#fjs-paywall-intro + div';
  let article = document.querySelector(article_sel);
  if (article) {
    article_src_sel += ', ' + article_sel;
    getArchive(url, article_sel + '[data-reduced="true"]', {rm_attrib: 'data-reduced'}, article_sel, '', article_src_sel);
  } else {
    article_sel = 'article#article-content';
    article_src_sel += ', ' + article_sel + ' > section';
    getArchive(url, article_sel + ' div[data-testid="premium"]', {rm_attrib: 'data-testid'}, article_sel + ' > section', '', article_src_sel, article_sel + ' > header');
    let ads = 'span[style*="background-color:"]:has(> span[style*="min-height:"])';
    hideDOMStyle(ads, 2);
  }
  let ads = 'div.dfp-space';
  hideDOMStyle(ads);
}

else if (matchDomain(nl_dpg_media_domains)) {
  setCookie('TID_ID', '', '', '/', 0);
  let banners = 'aside[data-temptation-position^="ARTICLE_"], div[data-temptation-position^="PAGE_"], div[class^="ad--"], div[id^="article_paragraph_"]';
  hideDOMStyle(banners);
  window.setTimeout(function () {
    let elem_hidden = document.querySelectorAll('[class^="artstyle__"][style="display: none;"]');
    for (let elem of elem_hidden)
      elem.removeAttribute('style');
  }, 500);
}

else if (matchDomain(nl_mediahuis_region_domains)) {
  let video = document.querySelector('div.video, div[data-testid="article-video"]');
  func_post = function () {
    let article = document.querySelector(article_sel);
    if (article) {
      if (video) {
        let video_new = article.querySelector('div[id$="-streamone"], div[id^="video-player-"], div[id^="player_"]');
        if (video_new && video_new.parentNode)
          video_new.parentNode.replaceChild(video, video_new);
        else {
          let header = article.querySelector('h1');
          let br = document.createElement('br');
          if (header)
            header.after(br, video, br);
        }
      }
      if (mobile) {
        let div_next = document.querySelector('div[id="__next"]');
        if (div_next)
          article.style.width = div_next.offsetWidth - 20 + 'px';
        let lazy_images = article.querySelectorAll('figure img[loading="lazy"][style]');
        for (let elem of lazy_images)
          elem.style = 'width: 95%;';
        let figures = article.querySelectorAll('figure div');
        for (let elem of figures) {
          elem.removeAttribute('style');
          let svg = elem.querySelector('svg');
          removeDOMElement(svg);
        }
      }
      if (article.innerText.length < 1000) {
        let header = article.querySelector('hgroup');
        if (header)
          header.before(googleSearchToolLink(url));
      }
    }
  }
  let paywall_sel = 'head > meta[name$="article_ispaidcontent"][content="true"]';
  let article_sel = 'main > article';
  let url = window.location.href;
  getArchive(url, paywall_sel, '', article_sel);
  window.setTimeout(function () {
    let noscroll = document.querySelector('body[class*="style_disable-scroll-popup"]');
    if (noscroll)
      noscroll.style = 'position: static !important; overflow: visible !important';
  }, 500);
  let banners = 'div[class*="style_popover"]';;
  hideDOMStyle(banners);
}

else if (matchDomain('nrc.nl')) {
  setCookie('counter', '', '', '/', 0, true);
  let banners = 'div[id$="modal__overlay"], div.header__subscribe-bar, div.banner, dialog.dmt-login-modal';
  hideDOMStyle(banners);
}

else if (matchDomain('telegraaf.nl')) {
  func_post = function () {
    if (mobile) {
      let article = document.querySelector('article');
      let body = document.querySelector('body');
      if (article && body) {
        article.style.width = body.offsetWidth * 0.95;
        let lazy_images = document.querySelectorAll('button > img[loading="lazy"]');
        for (let elem of lazy_images) {
          elem.style = 'width: 100%;';
          elem.parentNode.style['min-height'] = 'auto';
        }
      }
    }
    let gallery, img_width, captions, next, next_images, next_img_width;
    let gallery_new = document.createElement('div');
    let figure_nr = 0;
    let gallery_figures = document.querySelectorAll('div > ul > li > figure');
    for (let figure of gallery_figures) {
      if (!figure_nr) {
        gallery = figure.parentNode.parentNode.parentNode;
        captions = gallery.querySelectorAll('div > span > span');
        next = gallery.nextSibling;
        if (next)
          next_images = next.querySelectorAll('img[currentsourceurl]');
      }
      let img = figure.querySelector('img[currentsourceurl]');
      if (img && next_images) {
        let img_src = img.getAttribute('currentsourceurl');
        if (img_src) {
          if (img_src.includes('/alternates/'))
            img_width = img_src.split('/alternates/')[1].split('/')[0];
        } else if (img_width && next_images[figure_nr]) {
          img_src = next_images[figure_nr].getAttribute('currentsourceurl');
          if (img_src && img_src.includes('/alternates/')) {
            next_img_width = img_src.split('/alternates/')[1].split('/')[0];
            img_src = img_src.replace(next_img_width, img_width);
          }
        }
        let figure_new = makeFigure(img_src, captions && captions[figure_nr] ? captions[figure_nr].parentNode.innerText: '', {style: 'width: 100%;'});
        figure_new.style = 'margin: 20px 0px;';
        gallery_new.appendChild(figure_new);
      }
      figure_nr++;
    }
    if (gallery && next) {
      next.after(gallery_new);
      removeDOMElement(gallery, next);
    }
    let iframes = pageContains('div[style]', /^<iframe/);
    for (let elem of iframes) {
      let parser = new DOMParser();
      let doc = parser.parseFromString('<div>' + elem.innerText.replace(/”/g, '"') + '</div>', 'text/html');
      let elem_new = doc.querySelector('div');
      elem.parentNode.replaceChild(elem_new, elem);
    }
    let errors = document.querySelectorAll('div[old-src]:not([src]):has(div#__next_error__)');
    for (let elem of errors) {
      let elem_new = document.createElement('iframe');
      elem_new.src = elem.getAttribute('old-src');
      elem_new.style = 'width: 100%; height: ' + elem.getAttribute('height') + 'px;';
      elem.parentNode.replaceChild(elem_new, elem);
    }
    document.querySelectorAll('div > div[style^="min-height:"] > div[id^="player_"]').forEach(e => hideDOMElement(e.parentNode.parentNode));
  }
  let url = window.location.href;
  window.setTimeout(function () {
    let paywall_sel = 'div[data-testid="paywall-position-popover"]:not(:empty)';
    let paywall = document.querySelector(paywall_sel);
    if (paywall) {
      if (window.location.pathname.startsWith('/video/') && document.querySelector('div[data-testid="article-video"]'))
        removeDOMElement(paywall);
      else
        getArchive(url, paywall_sel, '', 'article');
    }
  }, 1000);
  let ads = 'div[id^="ad_"], div[class^="scrollable-ads"], iframe#ecommerce-ad-iframe, div[data-pym-src]';
  hideDOMStyle(ads);
}

else if (matchDomain('tijd.be')) {
  let url = window.location.href;
  func_post = function () {
    if (mobile) {
      document.querySelectorAll('figure img[loading="lazy"][style]').forEach(e => e.style = 'width: 95%;');
    }
  }
  if (matchDomain('belegger.tijd.be')) {
    if (window.location.pathname.endsWith('.html')) {
      getArchive(url, 'html.paywalled', {rm_class: 'paywalled'}, 'main');
      addStyle('body {overflow: auto !important}');
    }
    let banner = document.querySelector('div[data-id="react-paywall-auth0"]');
    removeDOMElement(banner);
  } else {
    let close_button = document.querySelector('button.ds-modal__top-bar__closebutton');
    if (close_button)
      close_button.click();
    getArchive(url, 'html.paywall-active', {rm_class: 'paywall-active'}, 'article');
  }
}

else if (matchDomain('vn.nl')) {
  let paywall = document.querySelectorAll('section[class^="c-paywall"]');
  if (paywall.length) {
    removeDOMElement(...paywall);
    let article = document.querySelector('div.c-article-content__container');
    if (article) {
      let json_script = document.querySelector('script#__NEXT_DATA__');
      if (json_script) {
        try {
          let json = JSON.parse(json_script.text);
          if (json && json.props.pageProps.article && json.props.pageProps.article.content) {
            let parser = new DOMParser();
            let doc = parser.parseFromString('<div>' + json.props.pageProps.article.content + '</div>', 'text/html');
            let content_new = doc.querySelector('div');
            article.innerHTML = '';
            article.appendChild(content_new);
            let audio = document.querySelector('div.c-author-info__audio-player');
            if (audio) {
              if (json.props.pageProps.article.audioplayer.audioFile.node.mediaItemUrl) {
                let audio_new = document.createElement('audio');
                audio_new.src = json.props.pageProps.article.audioplayer.audioFile.node.mediaItemUrl;
                audio_new.style = 'height: 50px; width: 60%;';
                audio_new.setAttribute('controls', '');
                audio.parentNode.replaceChild(audio_new, audio);
              }
            }
          } else
            refreshCurrentTab();
        } catch (err) {
          console.log(err);
        }
      }
    }
    let noscroll = document.querySelector('html[class]');
    if (noscroll)
      noscroll.removeAttribute('class');
  }
}

ads_hide();
leaky_paywall_unhide();

}, 1000);

// General Functions

// import (see @require)

})();
