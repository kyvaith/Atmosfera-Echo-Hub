/* Atmosfera's fixed-profile editor. HA owns validation and persistence; preview never calls entity actions. */
const AEH_TEXT = {
  en: {
    heading:"Screen editor",intro:"Make room for the things you reach for.",display:"Display",save:"Save layout",saving:"Saving…",
    saved:"Saved",sent:"Sent",applied:"Applied",unconfirmed:"Not confirmed",waiting:"Waiting",online:"Connected",offline:"Offline",unknown:"Unknown",
    received:"Received",snapshot:"Snapshot cache",ready:"Ready",olderLayout:"Older layout",differentLayout:"Different layout",lastKnown:"Last known",pendingPlaces:"{count} places waiting",statusHint:"Received and snapshot readiness describe cached device reports, not physical display confirmation. Off-screen pages may still be waiting.",
    cut:"Cut card",cutOf:"To move",cutHint:"The card stays in place until you paste it into an empty compatible place. Cut: Ctrl/Cmd+X · Paste: Ctrl/Cmd+V.",cutReady:"Card selected to move. Choose an empty compatible place, on either page, then paste.",cutChanged:"The source card changed. Cut it again before moving it.",pasteMove:"Move card here",movePasteEmpty:"A card can only be moved into an empty compatible place.",pasteMoved:"Card moved. Save when ready.",clearCut:"Cancel move",cutCleared:"Move selection cleared.",
    groupCut:"Cut selected",groupMove:"Move group…",groupMoveTitle:"Move {count} selected cards",groupCutOf:"Group to move",groupCutHint:"Cards stay in place until you confirm. Choose empty places or places belonging to this selected group.",groupCutReady:"Group selected to move. Map every destination and confirm when ready.",groupCutChanged:"The selected cards changed. Cut the group again before moving it.",groupMoveInvalid:"Choose distinct compatible empty places or places belonging to this selected group.",groupMoved:"Cards moved in the draft: {count}. Save when ready.",groupAlreadyThere:"The cards are already in the selected places.",
    groupCopy:"Copy selected",groupOf:"Copied group",groupCopied:"Copied cards: {count}. Map every destination when you paste.",groupHint:"Copies are snapshots. Choose a separate empty compatible place for each card; nothing is saved automatically.",groupPaste:"Paste group…",groupTitle:"Paste {count} copied cards",groupChoose:"Choose a destination",groupTarget:"Destination for {title}",groupUnavailable:"Selected place is no longer available",groupInvalid:"Review the group and choose distinct empty compatible places for every card.",groupChanged:"The layout or clipboard context changed. Open a new paste review.",groupIDs:"Could not prepare the copies. No cards were pasted.",groupPasted:"Copied cards pasted into the draft: {count}. Save when ready.",
    multiStart:"Select cards",multiDone:"Done selecting",multiClear:"Clear selection",multiPage:"Select this page",multiCount:"Selected: {count} · on this page: {page}",multiHint:"Select cards on either page. Changes stay in your draft until Save.",multiShow:"Show selected",multiHide:"Hide selected",multiDelete:"Delete selected",multiDeleteTitle:"Delete {count} cards from this draft?",multiDeleteHint:"Review the selected cards. Nothing is saved automatically; Undo restores the whole group.",multiDeleteConfirm:"Delete {count} cards",multiChanged:"The selection changed. Review it again.",multiNoChange:"The selected cards already have this visibility.",multiShown:"Cards shown in the draft: {count}. Save when ready.",multiHidden:"Cards hidden in the draft: {count}. Save when ready.",multiDeleted:"Cards removed from the draft: {count}. Save when ready.",multiKeyboard:"Space or Enter selects a card. Arrow keys move focus. Escape ends selection.",multiLimit:"Select at most 14 editable cards.",multiActive:"Card selection",multiExited:"Card selection ended.",
    copy:"Copy card",paste:"Paste copy here",clearCopy:"Clear copy",copyCleared:"The card copy was cleared.",copied:"Card copied. Select an empty compatible place, on either page, then paste.",pasted:"Card copied into this place. Save when ready.",copyHint:"Copy: Ctrl/Cmd+C · Paste: Ctrl/Cmd+V. Copies stay in this editor until you switch display or user.",pasteEmpty:"A copy can only be pasted into an empty compatible place.",copyOf:"Copied card",
    identityTitle:"Device details stored in Home Assistant",deviceName:"Device name",manufacturer:"Manufacturer",deviceModel:"Model",softwareVersion:"Software version (stored)",identityStored:"Last details stored in Home Assistant.",identityOffline:"The device’s current status cannot be confirmed.",identityMissing:"No stored details are available for this device.",
    capabilities:"Display profile and limits",profile:"Profile",resolution:"Resolution",places:"Places",pages:"Pages",editable:"editable",reservedPlaces:"reserved / hidden",builtInPages:"built-in",supported:"Supported",notSupported:"Not supported",profileHint:"This Home Assistant profile defines the editor's limits. It is not a detected firmware version or confirmation of device support.",featureMove:"Move / swap",featureResize:"Resize",featurePages:"Custom pages",featureControls:"Native controls",featureApplied:"Physical display acknowledgement",
    library:"Your Home Assistant",search:"Search entities",all:"All types",area:"Area / room",allAreas:"All areas",noArea:"No area",areaLimit:"Some areas are not listed. Use entity search to find more.",add:"Add to selected place",noEntities:"No matching entities.",
    loading:"Loading your screen…",noDevices:"No configured Atmosfera display was found.",retry:"Try again",
    security:"Security",controls:"Controls",home:"Clock & weather",apps:"Applications",reserved:"Built-in page",
    preview:"Layout preview",previewHint:"Live Home Assistant values. The preview does not control devices.",
    fixed:"Existing screen layout",fixedHint:"Card positions and sizes follow the screen's built-in profile.",
    inspector:"Card properties",selectCard:"Select a card or an empty place.",empty:"Add a card",hidden:"Hidden",emptySlot:"Empty place",
    selectedStyle:"Selected card style…",styleTitle:"Style of {count} selected cards",styleHint:"Choose one available color for the selected cards. This changes only the draft.",styleUnchanged:"Leave unchanged",styleApply:"Apply style",styleApplied:"Card style changed: {count}. Save when ready.",styleNoChange:"The selected cards already use this style.",styleChanged:"The selected cards or layout changed. Open a new style review.",styleInvalid:"Choose a color from the available list.",palettePrimary:"Accent",palettePrimaryContainer:"Accent container",paletteSecondary:"Secondary",paletteSurface:"Neutral",paletteTertiary:"Tertiary",
    sunPlacement:"Sun information needs a text tile; the two large value tiles cannot show its caption.",
    entity:"Entity",changeEntity:"Choose an entity from the library",title:"Title",icon:"Icon",palette:"Color",visible:"Show on screen",
    type:"Card type",entityType:"Entity",sensorType:"Information",actionType:"Action",tap:"On tap",default:"Default action",none:"Do nothing",
    service:"Configured action",chooseService:"Choose an action",noActions:"No supported action is available for this entity.",
    actionUnavailable:"This saved action is currently unavailable. Choose a supported action before saving.",
    controlProfileChanged:"The display profile changed. Reload the saved layout before choosing light controls.",
    numberControl:"Open Number stepper",numberUnsupported:"Number controls require matching firmware and a negotiated generic control channel.",numberEntity:"Choose a visible Entity card for an available input_number helper with an exact supported numeric domain.",numberHint:"Opens minus/plus controls. The preview sends no commands; Home Assistant rechecks the current value and step metadata.",numberReviewTitle:"Use Number controls?",numberReviewV2:"This changes the draft to layout v3 and opens Number controls for this card. Other cards are preserved. Nothing is saved yet.",numberReviewV3:"This card will open Number controls. Nothing is saved yet.",numberConfirm:"Use Number controls",numberNotice:"Number controls selected in the draft. Save the layout when ready.",
    control:"Open light controls",controlHint:"Opens the device's light controls. The preview never sends commands; On/Off and brightness are validated again by Home Assistant.",controlUnsupported:"Light controls require matching firmware and a connected, negotiated light-control channel. Existing tap actions are unchanged.",controlEntity:"Choose a visible Entity card for an available light with a supported power action.",controlBrightness:"Brightness is available when the light supports it. An unknown value is shown as --, never an invented percentage.",controlPowerOnly:"Brightness unavailable. Only the light's supported On/Off actions will be enabled.",controlReviewTitle:"Use light controls?",controlReviewV2:"This changes the draft to layout v3 and makes this card open light controls. All other card IDs, positions and actions are preserved. Older firmware keeps this card passive. Nothing is saved yet.",controlReviewV3:"This card will open light controls. Nothing is saved yet; review the draft and save when ready.",controlConfirm:"Use light controls",controlChanged:"The display, draft or light capability changed. Review the current card and try again.",controlNotice:"Light controls selected in the draft. Save the layout when ready.",
    parameters:"Action settings",optional:"Optional",required:"Required",true:"Yes",false:"No",rgb:"Red, green, blue (0–255)",
    move:"Move or swap",choosePlace:"Choose a place",remove:"Remove card",close:"Close",undo:"Undo",redo:"Redo",undone:"Change undone.",redone:"Change redone.",dirty:"Unsaved changes",
    clean:"All changes saved",export:"Export saved",import:"Import layout",exportHint:"The saved layout was exported. Unsaved changes are not included.",
    importTitle:"Review imported layout",importHint:"Nothing has been saved yet. Use this layout as a draft, then save when ready.",
    useImport:"Use as draft",cancel:"Cancel",cards:"cards",imported:"Imported as a draft.",invalidFile:"Choose a valid Atmosfera layout JSON file.",
    tooLarge:"This file exceeds this display's layout limit.",unsupported:"This backup format or version is not supported.",
    switchTitle:"Keep your changes?",switchHint:"This display has an unsaved draft.",saveSwitch:"Save and switch",discardSwitch:"Discard and switch",stay:"Keep editing",
    conflict:"A newer layout was saved elsewhere. Your draft is still here.",reload:"Reload saved layout",restore:"Restore my draft",
    recovered:"The saved layout is loaded. Your previous draft is kept until you leave this editor.",restored:"Your draft is restored against the loaded version. Review it before saving.",
    savedNotice:"Layout saved in Home Assistant.",saveFailed:"Could not save",catalogueFailed:"Could not load the entity library",
    drag:"Drag or press Space to pick up",picked:"Picked up. Choose a place with arrow keys or Tab, then press Enter. Escape cancels.",
    drop:"Drop here",moved:"Card moved.",assigned:"Entity assigned.",cancelled:"Move cancelled.",incompatible:"This place does not support that card.",
    chooseEmpty:"Choose a place on the preview first.",removed:"Card removed.",checkNumber:"Enter a number in the allowed range.",checkRgb:"Use three whole numbers from 0 to 255.",
    requiredValue:"Choose a value.",refreshFailed:"Device status could not be refreshed.",noEntity:"No entity selected",page:"Page",slot:"Place",
    matches:"matches",more:"Refine your search to see more.",actionsNote:"These settings configure a tap. They do not add a native slider to the screen.",
    importCount:"The imported layout contains",keyboard:"Move with a mouse, touch, or Space and arrow keys.",reloadFailed:"Could not reload",
  },
  pl: {
    heading:"Edytor ekranu",intro:"Najważniejsze rzeczy zawsze pod ręką.",display:"Ekran",save:"Zapisz układ",saving:"Zapisywanie…",
    saved:"Zapisano",sent:"Wysłano",applied:"Zastosowano",unconfirmed:"Brak potwierdzenia",waiting:"Oczekuje",online:"Połączony",offline:"Offline",unknown:"Nieznany",
    received:"Odebrano",snapshot:"Pamięć snapshotów",ready:"Gotowa",olderLayout:"Starszy układ",differentLayout:"Inny układ",lastKnown:"Ostatnio odczytane",pendingPlaces:"Oczekujące miejsca: {count}",statusHint:"Odebranie i gotowość snapshotów opisują zapamiętane raporty urządzenia, nie fizyczne wyświetlenie. Strony poza ekranem mogą nadal oczekiwać.",
    cut:"Wytnij kartę",cutOf:"Do przeniesienia",cutHint:"Karta pozostaje na miejscu, aż wkleisz ją w puste zgodne miejsce. Wytnij: Ctrl/Cmd+X · Wklej: Ctrl/Cmd+V.",cutReady:"Wybrano kartę do przeniesienia. Wybierz puste zgodne miejsce na dowolnej stronie i wklej.",cutChanged:"Karta źródłowa zmieniła się. Wytnij ją ponownie przed przeniesieniem.",pasteMove:"Przenieś kartę tutaj",movePasteEmpty:"Kartę można przenieść tylko w puste zgodne miejsce.",pasteMoved:"Przeniesiono kartę. Zapisz układ, gdy będzie gotowy.",clearCut:"Anuluj przenoszenie",cutCleared:"Anulowano wybór karty do przeniesienia.",
    groupCut:"Wytnij zaznaczone",groupMove:"Przenieś grupę…",groupMoveTitle:"Przenieś zaznaczone karty: {count}",groupCutOf:"Grupa do przeniesienia",groupCutHint:"Karty pozostają na miejscu do potwierdzenia. Wybierz puste miejsca lub miejsca należące do tej zaznaczonej grupy.",groupCutReady:"Wybrano grupę do przeniesienia. Wskaż każde miejsce docelowe i potwierdź, gdy będzie gotowa.",groupCutChanged:"Zaznaczone karty zmieniły się. Wytnij grupę ponownie przed przeniesieniem.",groupMoveInvalid:"Wybierz osobne zgodne puste miejsca lub miejsca należące do tej zaznaczonej grupy.",groupMoved:"Przeniesiono karty w szkicu: {count}. Zapisz układ, gdy będzie gotowy.",groupAlreadyThere:"Karty są już w wybranych miejscach.",
    groupCopy:"Kopiuj zaznaczone",groupOf:"Skopiowana grupa",groupCopied:"Skopiowano karty: {count}. Przy wklejaniu wybierz każde miejsce docelowe.",groupHint:"Kopie zachowują skopiowane dane. Dla każdej karty wybierz osobne puste zgodne miejsce; nic nie zapisuje się automatycznie.",groupPaste:"Wklej grupę…",groupTitle:"Wklej skopiowane karty: {count}",groupChoose:"Wybierz miejsce docelowe",groupTarget:"Miejsce dla: {title}",groupUnavailable:"Wybrane miejsce nie jest już dostępne",groupInvalid:"Sprawdź grupę i wybierz osobne puste zgodne miejsce dla każdej karty.",groupChanged:"Zmieniono układ lub kontekst schowka. Otwórz nowe potwierdzenie wklejania.",groupIDs:"Nie udało się przygotować kopii. Nie wklejono żadnej karty.",groupPasted:"Wklejono karty do szkicu: {count}. Zapisz układ, gdy będzie gotowy.",
    multiStart:"Zaznacz karty",multiDone:"Zakończ zaznaczanie",multiClear:"Wyczyść zaznaczenie",multiPage:"Zaznacz stronę",multiCount:"Zaznaczono: {count} · na tej stronie: {page}",multiHint:"Wybierz karty na dowolnej stronie. Zmiany pozostają w szkicu do zapisu.",multiShow:"Pokaż zaznaczone",multiHide:"Ukryj zaznaczone",multiDelete:"Usuń zaznaczone",multiDeleteTitle:"Usunąć ze szkicu: {count}?",multiDeleteHint:"Sprawdź wybrane karty. Nic nie zapisuje się automatycznie; Cofnij odtwarza całą grupę.",multiDeleteConfirm:"Usuń karty: {count}",multiChanged:"Zaznaczenie zmieniło się. Sprawdź je ponownie.",multiNoChange:"Zaznaczone karty mają już tę widoczność.",multiShown:"Pokazano karty w szkicu: {count}. Zapisz układ, gdy będzie gotowy.",multiHidden:"Ukryto karty w szkicu: {count}. Zapisz układ, gdy będzie gotowy.",multiDeleted:"Usunięto ze szkicu: {count}. Zapisz układ, gdy będzie gotowy.",multiKeyboard:"Spacja lub Enter zaznacza kartę. Strzałki przenoszą fokus. Escape kończy zaznaczanie.",multiLimit:"Możesz zaznaczyć najwyżej 14 edytowalnych kart.",multiActive:"Zaznaczanie kart",multiExited:"Zakończono zaznaczanie kart.",
    copy:"Kopiuj kartę",paste:"Wklej kopię tutaj",clearCopy:"Wyczyść kopię",copyCleared:"Wyczyszczono kopię karty.",copied:"Skopiowano kartę. Wybierz puste zgodne miejsce na dowolnej stronie i wklej.",pasted:"Wklejono kopię karty. Zapisz układ, gdy będzie gotowy.",copyHint:"Kopiuj: Ctrl/Cmd+C · Wklej: Ctrl/Cmd+V. Kopia pozostaje w edytorze do zmiany ekranu lub użytkownika.",pasteEmpty:"Kopię można wkleić tylko w pustym zgodnym miejscu.",copyOf:"Skopiowana karta",
    identityTitle:"Dane urządzenia zapisane w Home Assistant",deviceName:"Nazwa urządzenia",manufacturer:"Producent",deviceModel:"Model",softwareVersion:"Wersja oprogramowania (zapisana)",identityStored:"Ostatnie dane zapisane w Home Assistant.",identityOffline:"Nie można potwierdzić aktualnego stanu urządzenia.",identityMissing:"Brak zapisanych danych tego urządzenia.",
    capabilities:"Profil ekranu i ograniczenia",profile:"Profil",resolution:"Rozdzielczość",places:"Miejsca",pages:"Strony",editable:"edytowalne",reservedPlaces:"zarezerwowane / ukryte",builtInPages:"wbudowane",supported:"Obsługiwane",notSupported:"Nieobsługiwane",profileHint:"Ten profil Home Assistant określa ograniczenia edytora. Nie jest wykrytą wersją firmware ani potwierdzeniem możliwości urządzenia.",featureMove:"Przenoszenie / zamiana",featureResize:"Zmiana rozmiaru",featurePages:"Własne strony",featureControls:"Natywne regulatory",featureApplied:"Potwierdzenie fizycznego wyświetlenia",
    library:"Twój Home Assistant",search:"Szukaj encji",all:"Wszystkie typy",area:"Obszar / pomieszczenie",allAreas:"Wszystkie obszary",noArea:"Bez obszaru",areaLimit:"Nie wszystkie obszary są na liście. Użyj wyszukiwania encji, aby znaleźć więcej.",add:"Dodaj w wybranym miejscu",noEntities:"Brak pasujących encji.",
    loading:"Wczytywanie ekranu…",noDevices:"Nie znaleziono skonfigurowanego ekranu Atmosfera.",retry:"Spróbuj ponownie",
    security:"Bezpieczeństwo",controls:"Sterowanie",home:"Zegar i pogoda",apps:"Aplikacje",reserved:"Strona wbudowana",
    preview:"Podgląd układu",previewHint:"Bieżące stany z Home Assistant. Podgląd nie steruje urządzeniami.",
    fixed:"Układ Twojego ekranu",fixedHint:"Położenie i rozmiar kart odpowiadają wbudowanemu profilowi ekranu.",
    inspector:"Właściwości karty",selectCard:"Wybierz kartę lub puste miejsce.",empty:"Dodaj kartę",hidden:"Ukryta",emptySlot:"Puste miejsce",
    selectedStyle:"Wygląd zaznaczonych…",styleTitle:"Wygląd zaznaczonych kart: {count}",styleHint:"Wybierz jeden z dostępnych kolorów dla zaznaczonych kart. Zmiana dotyczy tylko szkicu.",styleUnchanged:"Nie zmieniaj",styleApply:"Zastosuj wygląd",styleApplied:"Zmieniono wygląd kart: {count}. Zapisz układ, gdy będzie gotowy.",styleNoChange:"Zaznaczone karty mają już ten wygląd.",styleChanged:"Zmieniono zaznaczone karty lub układ. Otwórz ponownie wybór wyglądu.",styleInvalid:"Wybierz kolor z dostępnej listy.",palettePrimary:"Akcent",palettePrimaryContainer:"Jasny akcent",paletteSecondary:"Drugorzędny",paletteSurface:"Neutralny",paletteTertiary:"Uzupełniający",
    sunPlacement:"Dane słońca wymagają kafelka tekstowego; dwa kafelki dużych wartości nie mieszczą opisu zdarzenia.",
    entity:"Encja",changeEntity:"Wybierz encję z biblioteki",title:"Tytuł",icon:"Ikona",palette:"Kolor",visible:"Pokaż na ekranie",
    type:"Typ karty",entityType:"Encja",sensorType:"Informacja",actionType:"Akcja",tap:"Po dotknięciu",default:"Akcja domyślna",none:"Bez działania",
    service:"Wybrana akcja",chooseService:"Wybierz akcję",noActions:"Ta encja nie ma obecnie obsługiwanych akcji.",
    actionUnavailable:"Zapisana akcja jest obecnie niedostępna. Przed zapisem wybierz obsługiwaną akcję.",
    controlProfileChanged:"Profil ekranu zmienił się. Wczytaj zapisany układ przed wybraniem sterowania światłem.",
    numberControl:"Otwórz sterowanie liczbą",numberUnsupported:"Sterowanie liczbą wymaga zgodnego firmware i uzgodnionego kanału sterowania encjami.",numberEntity:"Wybierz widoczną kartę Encja dla dostępnego pomocnika input_number z obsługiwaną dziedziną liczbową.",numberHint:"Otwiera przyciski minus/plus. Podgląd nie wysyła poleceń; Home Assistant ponownie sprawdza wartość i parametry kroku.",numberReviewTitle:"Użyć sterowania liczbą?",numberReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy sterowanie liczbą. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",numberReviewV3:"Ta karta otworzy sterowanie liczbą. Jeszcze nic nie zapisano.",numberConfirm:"Użyj sterowania liczbą",numberNotice:"Wybrano sterowanie liczbą w szkicu. Zapisz układ, gdy będzie gotowy.",
    control:"Otwórz sterowanie światłem",controlHint:"Otwiera sterowanie światłem na urządzeniu. Podgląd nie wysyła poleceń; Home Assistant ponownie sprawdza Włącz/Wyłącz i jasność.",controlUnsupported:"Sterowanie światłem wymaga zgodnego firmware oraz połączonego, uzgodnionego kanału sterowania. Dotychczasowe akcje dotknięcia pozostają bez zmian.",controlEntity:"Wybierz widoczną kartę Encja dla dostępnego światła z obsługiwaną akcją zasilania.",controlBrightness:"Jasność jest dostępna, gdy światło ją obsługuje. Nieznana wartość ma oznaczenie --, bez wymyślonego procentu.",controlPowerOnly:"Jasność niedostępna. Dostępne będą tylko obsługiwane akcje Włącz/Wyłącz.",controlReviewTitle:"Użyć sterowania światłem?",controlReviewV2:"Szkic przejdzie na układ v3, a ta karta będzie otwierać sterowanie światłem. Pozostałe identyfikatory, miejsca i akcje kart zostaną zachowane. Starszy firmware pozostawi tę kartę bez działania. Jeszcze nic nie zapisano.",controlReviewV3:"Ta karta będzie otwierać sterowanie światłem. Jeszcze nic nie zapisano; sprawdź szkic i zapisz go, gdy będzie gotowy.",controlConfirm:"Użyj sterowania światłem",controlChanged:"Ekran, szkic lub możliwości światła zmieniły się. Sprawdź bieżącą kartę i spróbuj ponownie.",controlNotice:"Wybrano sterowanie światłem w szkicu. Zapisz układ, gdy będzie gotowy.",
    parameters:"Ustawienia akcji",optional:"Opcjonalne",required:"Wymagane",true:"Tak",false:"Nie",rgb:"Czerwony, zielony, niebieski (0–255)",
    move:"Przenieś lub zamień",choosePlace:"Wybierz miejsce",remove:"Usuń kartę",close:"Zamknij",undo:"Cofnij",redo:"Ponów",undone:"Cofnięto zmianę.",redone:"Przywrócono zmianę.",dirty:"Niezapisane zmiany",
    clean:"Wszystkie zmiany zapisane",export:"Eksportuj zapisany",import:"Importuj układ",exportHint:"Wyeksportowano zapisany układ. Niezapisane zmiany nie są w nim zawarte.",
    importTitle:"Sprawdź importowany układ",importHint:"Jeszcze nic nie zapisano. Wczytaj układ jako szkic i zapisz go po sprawdzeniu.",
    useImport:"Wczytaj jako szkic",cancel:"Anuluj",cards:"kart",imported:"Wczytano jako szkic.",invalidFile:"Wybierz poprawny plik JSON z układem Atmosfera.",
    tooLarge:"Plik przekracza limit układu tego ekranu.",unsupported:"Nieobsługiwany format lub wersja kopii.",
    switchTitle:"Zachować zmiany?",switchHint:"Ten ekran ma niezapisany szkic.",saveSwitch:"Zapisz i przełącz",discardSwitch:"Odrzuć i przełącz",stay:"Edytuj dalej",
    conflict:"Gdzie indziej zapisano nowszy układ. Twój szkic jest zachowany.",reload:"Wczytaj zapisany układ",restore:"Przywróć mój szkic",
    recovered:"Wczytano zapisany układ. Poprzedni szkic jest zachowany do opuszczenia edytora.",restored:"Przywrócono szkic względem wczytanej wersji. Sprawdź go przed zapisem.",
    savedNotice:"Zapisano układ w Home Assistant.",saveFailed:"Nie udało się zapisać",catalogueFailed:"Nie udało się wczytać biblioteki encji",
    drag:"Przeciągnij lub naciśnij Spację",picked:"Podniesiono. Wybierz miejsce strzałkami lub Tab i naciśnij Enter. Escape anuluje.",
    drop:"Upuść tutaj",moved:"Przeniesiono kartę.",assigned:"Przypisano encję.",cancelled:"Anulowano przenoszenie.",incompatible:"To miejsce nie obsługuje tej karty.",
    chooseEmpty:"Najpierw wybierz miejsce w podglądzie.",removed:"Usunięto kartę.",checkNumber:"Podaj liczbę z dozwolonego zakresu.",checkRgb:"Podaj trzy liczby całkowite od 0 do 255.",
    requiredValue:"Wybierz wartość.",refreshFailed:"Nie udało się odświeżyć stanu urządzenia.",noEntity:"Nie wybrano encji",page:"Strona",slot:"Miejsce",
    matches:"wyników",more:"Zawęź wyszukiwanie, aby zobaczyć pozostałe.",actionsNote:"Te ustawienia określają akcję dotknięcia. Nie dodają suwaka na ekranie.",
    importCount:"Importowany układ zawiera",keyboard:"Przenoś myszą, dotykiem albo Spacją i strzałkami.",reloadFailed:"Nie udało się wczytać",
  },
};
const AEH_PALETTE_LABELS = Object.freeze({primary:"palettePrimary",primary_container:"palettePrimaryContainer",secondary:"paletteSecondary",surface:"paletteSurface",tertiary:"paletteTertiary"});
const AEH_ICONS = {action:"mdi:gesture-tap-button",alarm:"mdi:shield-home-outline",climate:"mdi:thermostat",cover:"mdi:blinds-horizontal",fan:"mdi:fan",light:"mdi:lightbulb-outline",lock:"mdi:lock-outline",scene:"mdi:palette-outline",speed:"mdi:speedometer",switch:"mdi:power",sensor:"mdi:thermometer",door:"mdi:window-closed-variant",presence:"mdi:account-group-outline",clock:"mdi:alarm",webhook:"mdi:webhook"};
const AEH_CLONE = value => JSON.parse(JSON.stringify(value));
const AEH_UUID = () => {
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
  // HA can be served over LAN HTTP, where randomUUID is unavailable.
  // getRandomValues remains available; card IDs are not credentials.
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
  const hex = Array.from(bytes, byte => byte.toString(16).padStart(2,"0")).join("");
  return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;
};
const AEH_COMPARE = value => JSON.stringify({version:value?.version,profile:value?.profile,cards:[...(value?.cards || [])].sort((a,b) => a.slot-b.slot)});
const AEH_ESCAPE = value => String(value ?? "").replaceAll("&","&amp;").replaceAll('"',"&quot;").replaceAll("<","&lt;").replaceAll(">","&gt;");
const AEH_DRAFT_FIELDS = new Set(["brightness_pct","color_temp_kelvin","rgb_color","percentage","oscillating","direction","preset_mode","position","tilt_position","temperature","target_temp_low","target_temp_high","hvac_mode","fan_mode","swing_mode","value","option"]);
const AEH_DRAFT_TEXT = {
  en:{title:"An unsaved draft is here",hint:"This browser kept your changes for this display. Restore them for review, or discard the local draft.",restore:"Restore draft",discard:"Discard draft",discarded:"The local draft was discarded.",restored:"Draft restored for review. Nothing has been saved to Home Assistant.",conflict:"This draft started at v{base}; the saved layout is now v{current}. Review the draft before replacing that version.",review:"Use reviewed draft",reviewed:"The draft is ready to save against the current version.",unavailable:"Browser draft recovery is unavailable. Saving to Home Assistant still works.",failed:"Could not restore the draft",invalid:"The saved browser draft is invalid or exceeds this display's limit.",local:"Draft kept in this browser"},
  pl:{title:"Masz niezapisany szkic",hint:"Ta przeglądarka zachowała zmiany dla tego ekranu. Przywróć je do sprawdzenia albo odrzuć lokalny szkic.",restore:"Przywróć szkic",discard:"Odrzuć szkic",discarded:"Odrzucono lokalny szkic.",restored:"Przywrócono szkic do sprawdzenia. Nic nie zapisano w Home Assistant.",conflict:"Szkic powstał na wersji v{base}; zapisany układ ma już v{current}. Sprawdź szkic przed zastąpieniem tej wersji.",review:"Użyj sprawdzonego szkicu",reviewed:"Szkic jest gotowy do zapisu względem bieżącej wersji.",unavailable:"Odzyskiwanie szkicu w przeglądarce jest niedostępne. Zapis w Home Assistant nadal działa.",failed:"Nie udało się przywrócić szkicu",invalid:"Zapisany szkic przeglądarki jest niepoprawny lub przekracza limit ekranu.",local:"Szkic zachowany w tej przeglądarce"},
};

class AtmosferaTileEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode:"open"});
    this._data = null; this._entryId = ""; this._draft = null; this._saved = null;
    this._undo = []; this._redo = []; this._selectedSlot = null; this._pageId = "";
    this._query = ""; this._domain = ""; this._area = ""; this._areas = []; this._areasTruncated = false; this._catalogue = []; this._entityIndex = new Map();
    this._status = {}; this._busy = false; this._loading = false; this._notice = ""; this._error = "";
    this._conflict = false; this._recovery = null; this._pending = null; this._fieldBefore = null; this._fieldErrors = {};
    this._drag = null; this._carry = null; this._catalogueRequest = 0; this._suppressClickUntil = 0;
    this._draftBaseRevision = null; this._draftOwner = null; this._restoreConflict = false;
    this._selectionEpoch = 0; this._loadRequest = 0; this._statusRequest = 0; this._paintedMarkup = new WeakMap();
    this._cardClipboard = null; this._profileStale = false;
    this._selectingCards = false; this._selectedCardIds = new Set(); this._cardSelectionScope = null;
    this.shadowRoot.addEventListener("click", event => this.onClick(event));
    this.shadowRoot.addEventListener("input", event => this.onInput(event));
    this.shadowRoot.addEventListener("change", event => this.onChange(event));
    this.shadowRoot.addEventListener("submit", event => event.preventDefault());
    this.shadowRoot.addEventListener("focusin", event => {
      if (event.target.dataset?.field) this._fieldBefore = AEH_CLONE(this._draft);
    });
    this.shadowRoot.addEventListener("keydown", event => this.onKeyDown(event));
    this.shadowRoot.addEventListener("pointerdown", event => this.onPointerDown(event));
    this._pointerMove = event => this.onPointerMove(event);
    this._pointerUp = event => this.onPointerUp(event);
    this._pointerCancel = () => this.cancelMove();
    this._beforeUnload = event => {
      this.persistDraft();
      if (this.dirty) { event.preventDefault(); event.returnValue = ""; }
    };
  }

  set hass(value) {
    const controlsBefore = this.lightControlAvailability().ready;
    if ((this._hass?.user?.id ?? null) !== (value?.user?.id ?? null)) { this.resetClipboardIntent(); this.resetCardSelection(); }
    if (this._hass?.user?.id && this._hass.user.id !== value?.user?.id) {
      this.persistDraft(); this._selectionEpoch++; this._loadRequest++;
      this._data = null; this._draft = null; this._saved = null; this._entryId = "";
      this._loading = false; this._busy = false; this._pending = null; this._entityIndex.clear();
      window.clearTimeout(this._draftTimer); this.cancelMove(false);
    }
    this._hass = value;
    if (this.isConnected && !this._data && !this._loading) this.load();
    else if (this._data) {
      this.paintValues();
      if (controlsBefore !== this.lightControlAvailability().ready) this.paintControlAvailability();
    }
  }
  set panel(value) { this._panel = value; }
  connectedCallback() {
    window.addEventListener("beforeunload", this._beforeUnload);
    this.render(); this.load();
    this._poll = window.setInterval(() => this.refreshStatus(), 5000);
  }
  disconnectedCallback() {
    this.resetCardSelection();
    this.resetClipboardIntent(); this._statusRequest++;
    this.persistDraft(); window.clearTimeout(this._draftTimer);
    window.removeEventListener("beforeunload", this._beforeUnload);
    window.clearInterval(this._poll); window.clearTimeout(this._queryTimer);
    this.cancelMove(false);
  }
  t(key) { return (AEH_TEXT[this._hass?.locale?.language?.startsWith("pl") || this._hass?.language?.startsWith("pl") ? "pl" : "en"][key] || key); }
  dt(key) { return AEH_DRAFT_TEXT[this._hass?.locale?.language?.startsWith("pl") || this._hass?.language?.startsWith("pl") ? "pl" : "en"][key]; }
  get entry() { return this._data?.entries.find(entry => entry.entry_id === this._entryId); }
  get profile() { return this.entry?.profile; }
  get dirty() { return !!this._draft && AEH_COMPARE(this._draft) !== AEH_COMPARE(this._saved); }
  get slots() { return (this.profile?.slots || []).filter(slot => slot.editable && !slot.hidden); }
  get pages() { return (this.profile?.pages || []).filter(page => this.slots.some(slot => slot.page_id === page.id)).sort((a,b) => a.order-b.order); }
  get pageSlots() { return this.slots.filter(slot => slot.page_id === this._pageId).sort((a,b) => a.y-b.y || a.x-b.x); }
  cardAt(slot) { return this._draft?.cards.find(card => card.slot === Number(slot)); }
  slotAt(slot) { return this.slots.find(item => item.slot === Number(slot)); }
  entityFor(id) { return this._entityIndex.get(id); }
  icon(name, extra="") { return `<ha-icon icon="${AEH_ESCAPE(AEH_ICONS[name] || name)}" ${extra}></ha-icon>`; }
  errorText(error) {
    const seen = new Set();
    const visit = value => {
      if (typeof value === "string") return value;
      if (value === null || typeof value !== "object" || seen.has(value)) return "";
      seen.add(value);
      for (const key of ["message","code","error","body"]) { const found = visit(value[key]); if (found) return found; }
      try { return JSON.stringify(value); } catch (_ignored) { return ""; }
    };
    return visit(error) || "Unknown error";
  }
  async ws(command, data={}) { return this._hass.callWS({type:`atmosfera_echo_hub/${command}`,...data}); }

  async load() {
    if (!this._hass || this._loading) return;
    this._loading = true; const request = ++this._loadRequest;
    try {
      const result = await this.ws("layout/get");
      if (request !== this._loadRequest) return;
      this._data = result;
      const entry = result.entries.find(item => item.entry_id === this._entryId) || result.entries[0];
      if (entry) this.selectEntry(entry.entry_id);
      else this.render();
      this._error = "";
    } catch (error) { if (request === this._loadRequest) { this._error = this.errorText(error); this.render(); } }
    finally { if (request === this._loadRequest) this._loading = false; }
  }
  selectEntry(id) {
    this.resetCardSelection();
    this.resetClipboardIntent();
    if (this._draft && this._entryId && id !== this._entryId) this.persistDraft();
    this._selectionEpoch++;
    this._entryId = id;
    const entry = this.entry;
    if (!entry) return;
    this._saved = AEH_CLONE(entry.layout); this._draft = AEH_CLONE(entry.layout);
    this._status = {...entry.status}; this._statusError = false; this._profileStale = false; this._undo = []; this._redo = [];
    this._selectedSlot = null; this._pageId = this.pages[0]?.id || "";
    this._conflict = false; this._recovery = null; this._pending = null; this._fieldErrors = {};
    this._notice = ""; this._error = ""; this._carry = null; this._fieldBefore = null;
    this._draftBaseRevision = entry.layout.revision; this._draftOwner = this._hass?.user?.id;
    this._restoreConflict = false; this._storageError = false; this._storedDraft = null; this._draftStored = false;
    this._query = ""; this._domain = ""; this._area = ""; this._areas = []; this._areasTruncated = false; this._catalogue = []; this._entityIndex.clear();
    this.render(); this.fetchCatalogue(); this.offerStoredDraft();
  }
  requestSwitch(id) {
    if (id === this._entryId) return;
    if (!this.dirty) return this.selectEntry(id);
    this._pending = {kind:"switch",entryId:id}; this.renderModal();
    const picker = this.shadowRoot.querySelector("#device"); if (picker) picker.value = this._entryId;
  }
  draftPrefix() {
    const user = this._hass?.user?.id;
    return typeof user === "string" && user ? `atmosfera-layout-draft:v1:${encodeURIComponent(user)}:` : null;
  }
  draftKey() {
    const prefix = this.draftPrefix();
    return prefix && this._entryId && this.profile ? `${prefix}${encodeURIComponent(this._entryId)}:${encodeURIComponent(this.profile.id)}` : null;
  }
  draftLimit() { return Math.min(this.profile?.max_document_bytes || 32768,32768); }
  validateStoredDraft(record) {
    const object = value => !!value && typeof value === "object" && !Array.isArray(value);
    const keys = (value,allowed) => object(value) && Object.keys(value).every(key => allowed.includes(key));
    const fail = () => { throw new Error(this.dt("invalid")); };
    if (!keys(record,["version","profile","base_revision","updated_at","layout"]) || record.version !== 1 || record.profile !== this.profile.id || !Number.isSafeInteger(record.base_revision) || record.base_revision < 0 || !Number.isFinite(record.updated_at)) fail();
    const layout = record.layout;
    if (!keys(layout,["version","profile","cards"]) || ![2,3].includes(layout.version) || (layout.version === 3 && (!Array.isArray(this.profile.layout_versions) || !this.profile.layout_versions.includes(3))) || layout.profile !== this.profile.id || !Array.isArray(layout.cards) || layout.cards.length > this.profile.max_cards) fail();
    const ids = new Set(), slots = new Set();
    for (const card of layout.cards) {
      if (!keys(card,["id","slot","type","entity_id","title","icon","palette","visible","action"]) || typeof card.id !== "string" || !/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(card.id) || !Number.isInteger(card.slot) || ids.has(card.id) || slots.has(card.slot)) fail();
      const slot = this.profile.slots.find(item => item.slot === card.slot);
      if (this.isSunCard(card) && !this.acceptsCard(slot,card)) throw new Error(this.t("sunPlacement"));
      if (!slot || !this.acceptsCard(slot,card) || typeof card.visible !== "boolean" || (!slot.editable && card.visible) || typeof card.entity_id !== "string" || card.entity_id.length > 128 || (card.entity_id && !/^[a-z_][a-z0-9_]*\.[a-z0-9_]+$/.test(card.entity_id)) || typeof card.title !== "string" || [...card.title].length > 40 || !this._data.icons.includes(card.icon) || !this._data.palettes.includes(card.palette)) fail();
      ids.add(card.id); slots.add(card.slot);
      const action = card.action;
      if (!keys(action,["kind","service","data","control"]) || !["none","default","service","control"].includes(action.kind) || (card.type === "sensor" && action.kind !== "none")) fail();
      if (action.kind === "control") {
        if (layout.version !== 3 || Object.keys(action).length !== 2 || !((action.control === "light" && card.entity_id.startsWith("light.")) || (action.control === "number" && card.entity_id.startsWith("input_number."))) || card.type !== "entity" || !slot.editable || slot.hidden || card.slot < 2) fail();
        continue;
      }
      if (Object.hasOwn(action,"control")) fail();
      if (action.kind !== "service") { if (Object.keys(action).length !== 1) fail(); continue; }
      if (typeof action.service !== "string" || !/^[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*$/.test(action.service) || !object(action.data)) fail();
      for (const [key,value] of Object.entries(action.data)) {
        if (!AEH_DRAFT_FIELDS.has(key)) fail();
        if (Array.isArray(value)) { if (key !== "rgb_color" || value.length !== 3 || value.some(channel => !Number.isInteger(channel) || channel < 0 || channel > 255)) fail(); }
        else if (typeof value === "string") { if (!value || value.length > 128) fail(); }
        else if (typeof value === "number") { if (!Number.isFinite(value)) fail(); }
        else if (typeof value !== "boolean") fail();
      }
    }
    if (new TextEncoder().encode(JSON.stringify(record)).length > this.draftLimit()) fail();
    return record;
  }
  scheduleDraft() {
    window.clearTimeout(this._draftTimer);
    if (this.draftKey()) this._draftTimer = window.setTimeout(() => this.persistDraft(),250);
  }
  persistDraft() {
    const key = this.draftKey();
    if (!key || !this._draft || this._draftOwner !== this._hass?.user?.id) return false;
    try {
      const storage = window.localStorage;
      if (!storage) return false;
      const draft = this.dirty ? this._draft : this._recovery && AEH_COMPARE(this._recovery) !== AEH_COMPARE(this._saved) ? this._recovery : null;
      if (!draft) { if (this._storedDraft) return true; storage.removeItem(key); this._draftStored = false; return true; }
      if (Object.keys(this._fieldErrors).length) return false;
      const layout = AEH_CLONE(draft); delete layout.revision;
      const base = this.dirty ? this._draftBaseRevision : this._recoveryBaseRevision;
      const record = {version:1,profile:this.profile.id,base_revision:base ?? this._saved.revision,updated_at:Date.now(),layout};
      try { this.validateStoredDraft(record); } catch (_invalid) { return false; }
      storage.setItem(key,JSON.stringify(record));
      const siblings = [];
      for (let index=0;index<storage.length;index++) {
        const sibling = storage.key(index); if (sibling?.startsWith(this.draftPrefix()) && sibling !== key) siblings.push(sibling);
      }
      const dated = siblings.map(sibling => { try { return {key:sibling,date:JSON.parse(storage.getItem(sibling)).updated_at || 0}; } catch (_invalid) { return {key:sibling,date:0}; } }).sort((a,b) => a.date-b.date);
      while (dated.length >= 8) storage.removeItem(dated.shift().key);
      this._draftStored = true; this._storageError = false; this.paintToolbar(); return true;
    } catch (_unavailable) { this._storageError = true; this._draftStored = false; this.paintFeedback(); return false; }
  }
  clearStoredDraft() {
    const key = this.draftKey(); if (!key) return;
    window.clearTimeout(this._draftTimer);
    try { window.localStorage?.removeItem(key); } catch (_unavailable) { this._storageError = true; }
    this._storedDraft = null; this._draftStored = false;
  }
  offerStoredDraft() {
    const key = this.draftKey(); if (!key || this.dirty) return;
    try {
      const raw = window.localStorage?.getItem(key); if (!raw) return;
      if (new TextEncoder().encode(raw).length > this.draftLimit()) throw new Error(this.dt("invalid"));
      const record = this.validateStoredDraft(JSON.parse(raw));
      if (AEH_COMPARE(record.layout) === AEH_COMPARE(this._saved)) { this.clearStoredDraft(); return; }
      this._storedDraft = record; this._pending = {kind:"restore",record}; this.renderModal();
    } catch (error) { this._storageError = true; this._error = this.errorText(error); this.paintFeedback(); }
  }
  async restoreStoredDraft() {
    const record = this._pending?.kind === "restore" ? this._pending.record : null;
    if (!record || this._busy) return false;
    const id = this._entryId, epoch = this._selectionEpoch;
    this._statusRequest++; this._busy = true; this._error = ""; this.paintToolbar();
    try {
      this.validateStoredDraft(record);
      const result = await this.ws("layout/import",{entry_id:id,expected_revision:this._saved.revision,backup:{format:"atmosfera-layout",version:1,layout:record.layout},dry_run:true});
      if (id !== this._entryId || epoch !== this._selectionEpoch) return false;
      this._pending = null; this._storedDraft = null; this._busy = false;
      const document = AEH_CLONE(result.layout); document.revision = this._saved.revision;
      this.resetCardSelection(); this.mutate(() => { this._draft = document; });
      this._draftBaseRevision = record.base_revision;
      this._restoreConflict = record.base_revision !== this._saved.revision && this.dirty;
      this._conflict = this._restoreConflict; this._notice = this.dt("restored");
      this.persistDraft(); this.render(); return true;
    } catch (error) {
      if (epoch !== this._selectionEpoch) return false;
      this._error = `${this.dt("failed")}: ${this.errorText(error)}`; this.paintFeedback(); return false;
    } finally { if (epoch === this._selectionEpoch) { this._busy = false; this.paintToolbar(); } }
  }
  discardStoredDraft() {
    this.clearStoredDraft(); this._pending = null; this._notice = this.dt("discarded"); this.renderModal(); this.paintFeedback();
  }
  reviewRestoredDraft() {
    if (!this._restoreConflict) return;
    this._draftBaseRevision = this._saved.revision; this._restoreConflict = false; this._conflict = false;
    this._notice = this.dt("reviewed"); this.persistDraft(); this.paintFeedback(); this.paintToolbar();
  }
  async refreshStatus() {
    if (!this._entryId || this._busy || !this.isConnected) return;
    const id = this._entryId, epoch = this._selectionEpoch, revision = this._saved?.revision, request = ++this._statusRequest;
    const controlsBefore = this.lightControlAvailability().ready;
    const appearanceBefore = JSON.stringify([this.entry?.accent_color,this.entry?.colors]);
    try {
      const result = await this.ws("layout/get",{entry_id:id});
      if (id !== this._entryId || epoch !== this._selectionEpoch || revision !== this._saved?.revision || request !== this._statusRequest || this._busy || !this.isConnected) return;
      const latest = result.entries[0]; if (!latest) return;
      if (latest.profile && JSON.stringify(latest.profile) !== JSON.stringify(this.profile)) {
        // Profile migration remains an explicit reload. Never carry a copied
        // card into a different server definition reported by a status poll.
        this._profileStale = true; this.resetClipboardIntent(); this.resetCardSelection(); this.paintClipboard(); this.paintPreview(); this.paintCardSelection(); this.renderModal(); this.paintInspector();
      }
      this._status = {...latest.status}; this._statusError = false;
      Object.assign(this.entry,{status:latest.status,accent_color:latest.accent_color,colors:latest.colors,device_identity:latest.device_identity});
      if (latest.layout.revision !== this._saved.revision) {
        this.entry.layout = AEH_CLONE(latest.layout);
        if (this.dirty) { this._restoreConflict = false; this._conflict = true; this.paintFeedback(); }
        else {
          this.resetCardSelection(); this._saved = AEH_CLONE(latest.layout); this._draft = AEH_CLONE(latest.layout);
          this._undo = []; this._redo = []; this.render();
        }
      }
      if (appearanceBefore !== JSON.stringify([this.entry?.accent_color,this.entry?.colors])) this.paintAppearance();
      this.paintStatus(); this.paintCardSelection();
      if (controlsBefore !== this.lightControlAvailability().ready) this.paintControlAvailability();
    } catch (_error) {
      if (id !== this._entryId || epoch !== this._selectionEpoch || revision !== this._saved?.revision || request !== this._statusRequest || this._busy || !this.isConnected) return;
      this._statusError = true; this.paintStatus();
      if (controlsBefore !== this.lightControlAvailability().ready) this.paintControlAvailability();
    }
  }
  async fetchCatalogue() {
    if (!this._entryId) return;
    const request = ++this._catalogueRequest, id = this._entryId, epoch = this._selectionEpoch;
    try {
      const result = await this.ws("catalogue/get",{entry_id:id,query:this._query,limit:200,...(this._domain ? {domains:[this._domain]} : {}),...(this._area === "none" ? {area_id:""} : this._area.startsWith("area:") ? {area_id:this._area.slice(5)} : {})});
      if (id !== this._entryId || epoch !== this._selectionEpoch || request !== this._catalogueRequest) return;
      const entities = result.entities || [], completeAreas = Array.isArray(result.areas);
      const areas = this.catalogueAreas(completeAreas ? result.areas : entities);
      this._areasTruncated = result.areas_truncated === true || (!completeAreas && result.truncated === true);
      if (this._area.startsWith("area:") && !areas.some(area => this._area === `area:${area.area_id}`)) {
        // Only an authoritative complete facet list can prove that an area was
        // removed. A truncated/older catalogue must not silently widen a filter.
        if (completeAreas && !this._areasTruncated) { this._area = ""; return this.fetchCatalogue(); }
        const id = this._area.slice(5), previous = this._areas.find(area => area.area_id === id);
        areas.push(previous || {area_id:id,area_name:id});
      }
      this._areas = areas;
      this._catalogue = entities; this._catalogueTotal = result.total; this._truncated = result.truncated;
      for (const entity of this._catalogue) this._entityIndex.set(entity.entity_id,entity);
      this._catalogueError = ""; this.paintLibrary();
      if (!this.shadowRoot.querySelector(".inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
    } catch (error) {
      if (id !== this._entryId || epoch !== this._selectionEpoch || request !== this._catalogueRequest) return;
      this._catalogueError = this.errorText(error); this.paintLibrary();
    }
  }
  async fetchSelectedEntity() {
    const card = this.cardAt(this._selectedSlot), id = this._entryId, epoch = this._selectionEpoch;
    if (!card?.entity_id || this.entityFor(card.entity_id)) return;
    const entityId = card.entity_id;
    try {
      const result = await this.ws("catalogue/get",{entry_id:id,query:entityId,limit:20});
      if (id !== this._entryId || epoch !== this._selectionEpoch) return;
      for (const entity of result.entities || []) this._entityIndex.set(entity.entity_id,entity);
      if (this.cardAt(this._selectedSlot)?.entity_id === entityId && !this.shadowRoot.querySelector(".inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
    } catch (_ignored) { /* A saved entity remains editable while the catalogue is unavailable. */ }
  }
  pushHistory(before) {
    if (AEH_COMPARE(before) === AEH_COMPARE(this._draft)) return false;
    this._undo.push(before); if (this._undo.length > 60) this._undo.shift();
    this._redo = []; this._notice = ""; this._error = ""; this.scheduleDraft(); return true;
  }
  mutate(change) {
    if (!this._draft || this._busy) return false;
    const before = AEH_CLONE(this._draft), wasDirty = this.dirty; change(this._draft);
    if (!wasDirty) this._draftBaseRevision = this._saved.revision;
    const changed = this.pushHistory(before); this._fieldBefore = null; this._fieldErrors = {};
    if (changed) this.render();
    return changed;
  }
  history(direction) {
    this.finishField();
    const source = direction === "undo" ? this._undo : this._redo;
    const target = direction === "undo" ? this._redo : this._undo;
    if (!source.length || this._busy) return;
    this.resetCardSelection(); target.push(AEH_CLONE(this._draft)); this._draft = source.pop();
    this._notice = this.t(direction === "undo" ? "undone" : "redone"); this._error = "";
    this._fieldErrors = {}; this.render(); this.fetchSelectedEntity(); this.scheduleDraft();
  }
  selectSlot(slot) {
    if (this._selectingCards) return this.toggleCardSelection(slot);
    if (!this.slotAt(slot)) return;
    this.finishField(); this._selectedSlot = Number(slot); this._error = "";
    this.render(); this.focusSlot(slot); this.fetchSelectedEntity();
  }
  isSunCard(card) { return typeof card?.entity_id === "string" && card.entity_id.startsWith("sun."); }
  acceptsCard(place, card) {
    if (!place || !Array.isArray(place.types) || !place.types.includes(card?.type)) return false;
    if (!this.isSunCard(card)) return true;
    const allowed = this.profile?.sun_text_slots;
    return card.type === "sensor" && card.action?.kind === "none" && Object.keys(card.action).length === 1 &&
      place.editable === true && place.hidden !== true && Array.isArray(allowed) && allowed.length > 0 && allowed.length <= 14 &&
      allowed.every(Number.isInteger) && new Set(allowed).size === allowed.length && allowed.includes(place.slot);
  }
  sunLayoutAllowed(layout) {
    return !Array.isArray(layout?.cards) || layout.cards.every(card => !this.isSunCard(card) || this.acceptsCard(this.slotAt(card.slot), card));
  }
  refuseSunPlacement() {
    this._error = this.t("sunPlacement"); this.paintFeedback(); this.announce(this._error); return false;
  }
  newCard(entity, slot) {
    const domain = entity.entity_id.split(".")[0];
    const information = ["sensor","binary_sensor","person","sun"].includes(domain);
    const action = ["scene","script","button","input_button","automation"].includes(domain);
    const icon = ({sun:"clock",light:"light",climate:"climate",cover:"cover",lock:"lock",alarm_control_panel:"alarm",fan:"fan",scene:"scene",switch:"switch",input_boolean:"switch"})[domain] || "action";
    return {id:`card-${AEH_UUID()}`,slot:Number(slot),type:information ? "sensor" : action ? "action" : "entity",entity_id:entity.entity_id,
      title:[...(entity.name || entity.entity_id)].slice(0,40).join(""),icon,palette:information ? "surface" : "primary",visible:true,action:{kind:information ? "none" : "default"}};
  }
  assignEntity(entityId, slot=this._selectedSlot) {
    if (this._selectingCards) return false;
    const entity = this.entityFor(entityId);
    if (!entity) return false;
    if (slot === null || slot === undefined) slot = this.pageSlots.find(item => !this.cardAt(item.slot) &&
      (!this.isSunCard(entity) || this.acceptsCard(item,{entity_id:entity.entity_id,type:"sensor",action:{kind:"none"}})))?.slot;
    const target = this.slotAt(slot); if (!target) {
      if (this.isSunCard(entity)) return this.refuseSunPlacement();
      this.announce(this.t("chooseEmpty")); return false;
    }
    const card = this.newCard(entity,slot);
    if (!this.acceptsCard(target,card)) {
      if (this.isSunCard(card)) return this.refuseSunPlacement();
      this.announce(this.t("incompatible")); return false;
    }
    this._selectedSlot = target.slot;
    const changed = this.mutate(layout => { layout.cards = layout.cards.filter(item => item.slot !== target.slot); layout.cards.push(card); });
    if (changed) this.announce(this.t("assigned"));
    return changed;
  }
  moveCard(from,to) {
    if (this._selectingCards) return false;
    from = Number(from); to = Number(to);
    const source = this.cardAt(from), other = this.cardAt(to), a = this.slotAt(from), b = this.slotAt(to);
    if (!source || !a || !b || from === to) return false;
    if (!this.acceptsCard(b,source) || (other && !this.acceptsCard(a,other))) {
      if (this.isSunCard(source) || this.isSunCard(other)) return this.refuseSunPlacement();
      return false;
    }
    this._selectedSlot = to; this._pageId = b.page_id;
    const changed = this.mutate(() => { source.slot = to; if (other) other.slot = from; });
    if (changed) this.announce(this.t("moved"));
    return changed;
  }
  removeCard() {
    if (this._selectingCards) return false;
    const slot = this._selectedSlot; if (!this.slotAt(slot)) return;
    if (this.mutate(layout => { layout.cards = layout.cards.filter(card => card.slot !== slot); })) this.announce(this.t("removed"));
  }
  resetCardSelection() {
    const changed = this._selectingCards || this._selectedCardIds.size > 0;
    this._selectingCards = false; this._selectedCardIds.clear(); this._cardSelectionScope = null;
    if (["bulk-delete","bulk-style"].includes(this._pending?.kind)) this._pending = null;
    return changed;
  }
  syncCardSelection() {
    if (this._selectingCards && (this.clipboardDisconnected() || this._profileStale || this._cardSelectionScope !== this.clipboardScope() || !this.selectionCards())) return this.resetCardSelection();
    return false;
  }
  cardForSelection(slot) {
    const card = this.cardAt(slot), place = this.slotAt(slot);
    return card && typeof card.id === "string" && card.id && place && this.acceptsCard(place,card) && this._draft.cards.filter(item => item.id === card.id).length === 1 ? card : null;
  }
  selectionCards() {
    if (!this._selectingCards || !this._draft || this._selectedCardIds.size > 14) return null;
    const cards = [];
    for (const id of this._selectedCardIds) {
      const found = this._draft.cards.filter(card => card.id === id);
      if (found.length !== 1 || this.cardForSelection(found[0].slot) !== found[0]) return null;
      cards.push(found[0]);
    }
    return cards;
  }
  cardSelectionAllowed(ownDelete=false,ownStyle=false) {
    this.syncCardSelection();
    return this._selectingCards && !this._busy && !this._drag && !this._carry && !this._conflict &&
      (!this._pending || (ownDelete && this._pending.kind === "bulk-delete") || (ownStyle && this._pending.kind === "bulk-style")) && !Object.keys(this._fieldErrors).length;
  }
  startCardSelection() {
    if (this._busy || this._pending || this._drag || this._carry || this._conflict || this._profileStale || this.clipboardDisconnected() || !this._draft) return false;
    this.finishField(); if (Object.keys(this._fieldErrors).length) return false;
    this._selectingCards = true; this._selectedCardIds.clear(); this._cardSelectionScope = this.clipboardScope();
    this.resetClipboardIntent(); this._selectedSlot = null;
    this.paintClipboard(); this.paintPreview(); this.paintInspector(); this.paintToolbar(); this.announce(this.t("multiHint"));
    const first = this.pageSlots.find(slot => this.cardForSelection(slot.slot)); if (first) this.focusSlot(first.slot); return true;
  }
  endCardSelection() {
    const changed = this.resetCardSelection();
    if (changed) { this.paintPreview(); this.paintInspector(); this.renderModal(); this.paintToolbar(); this.announce(this.t("multiExited")); this.shadowRoot.querySelector('[data-action="selection-start"]')?.focus(); }
    return changed;
  }
  toggleCardSelection(slot) {
    if (!this.cardSelectionAllowed()) return false;
    const card = this.cardForSelection(slot); if (!card) return false;
    if (this._selectedCardIds.has(card.id)) this._selectedCardIds.delete(card.id);
    else if (this._selectedCardIds.size < 14) this._selectedCardIds.add(card.id);
    else { this.announce(this.t("multiLimit")); return false; }
    this.paintPreview(); this.paintToolbar(); this.focusSlot(slot); return true;
  }
  selectPageCards() {
    if (!this.cardSelectionAllowed()) return false;
    const cards = this.pageSlots.map(slot => this.cardForSelection(slot.slot)).filter(Boolean);
    const ids = new Set([...this._selectedCardIds,...cards.map(card => card.id)]);
    if (ids.size > 14 || cards.some(card => this._draft.cards.filter(item => item.id === card.id).length !== 1)) return false;
    this._selectedCardIds = ids; this.paintPreview(); this.paintToolbar(); return true;
  }
  clearCardSelection() {
    if (!this.cardSelectionAllowed()) return false;
    this._selectedCardIds.clear(); this.paintPreview(); this.paintToolbar(); return true;
  }
  selectionCandidate(change) {
    const candidate = AEH_CLONE(this._draft); change(candidate);
    if (new TextEncoder().encode(JSON.stringify(candidate)).length > this.draftLimit()) { this._error = this.t("tooLarge"); this.paintFeedback(); return null; }
    return candidate;
  }
  setSelectedVisibility(visible) {
    this.finishField();
    if (typeof visible !== "boolean" || !this.cardSelectionAllowed()) return false;
    const cards = this.selectionCards(); if (!cards?.length) return false;
    const count = cards.filter(card => card.visible !== visible).length;
    if (!count) { this._notice = this.t("multiNoChange"); this.paintFeedback(); this.announce(this._notice); return false; }
    const ids = new Set(cards.map(card => card.id)), change = layout => layout.cards.forEach(card => { if (ids.has(card.id)) card.visible = visible; });
    if (!this.selectionCandidate(change)) return false;
    const changed = this.mutate(change);
    if (changed) { this._notice = this.t(visible ? "multiShown" : "multiHidden").replace("{count}",count); this.paintFeedback(); this.announce(this._notice); this.shadowRoot.querySelector(`[data-action="${visible ? "batch-show" : "batch-hide"}"]`)?.focus(); }
    return changed;
  }
  stylePalettes() {
    return [...new Set((Array.isArray(this._data?.palettes) ? this._data.palettes : []).filter(name => Object.hasOwn(AEH_PALETTE_LABELS,name)))];
  }
  requestSelectedStyle() {
    this.finishField(); if (!this.cardSelectionAllowed()) return false;
    const cards = this.selectionCards(), palettes = this.stylePalettes();
    if (!cards?.length || cards.some(card => this._draft.cards.filter(item => item.slot === card.slot).length !== 1) || !palettes.length || !Number.isSafeInteger(this._saved?.revision) || this._saved.revision < 0 || this.entry?.layout?.revision !== this._saved.revision || ![2,3].includes(this._draft.version)) return false;
    this._pending = {kind:"bulk-style",scope:this.clipboardScope(),epoch:this._selectionEpoch,revision:this._saved.revision,version:this._draft.version,cards:AEH_CLONE(cards),palettes,palette:null};
    this._error = ""; this.renderModal(); this.paintToolbar(); return true;
  }
  selectedStyleCurrent() {
    const pending = this._pending;
    if (pending?.kind !== "bulk-style" || !this.cardSelectionAllowed(false,true) || pending.scope !== this.clipboardScope() || pending.epoch !== this._selectionEpoch ||
        pending.revision !== this._saved?.revision || pending.revision !== this.entry?.layout?.revision || pending.version !== this._draft.version ||
        JSON.stringify(pending.palettes) !== JSON.stringify(this.stylePalettes()) || !Array.isArray(pending.cards) || !pending.cards.length) return false;
    const cards = this.selectionCards();
    return cards?.length === pending.cards.length && cards.every(card => this._draft.cards.filter(item => item.slot === card.slot).length === 1 && pending.cards.some(prior => prior.id === card.id && JSON.stringify(prior) === JSON.stringify(card)));
  }
  selectedStyleReady() { return this.selectedStyleCurrent() && typeof this._pending.palette === "string" && this._pending.palettes.includes(this._pending.palette); }
  setSelectedStyle(value) {
    if (!this.selectedStyleCurrent()) { this._error = this.t("styleChanged"); this.paintFeedback(); this.paintToolbar(); return false; }
    if (typeof value !== "string") { this._error = this.t("styleInvalid"); this.paintFeedback(); return false; }
    const palette = value === "" ? null : value;
    if (palette !== null && (typeof palette !== "string" || !this._pending.palettes.includes(palette))) { this._error = this.t("styleInvalid"); this.paintFeedback(); return false; }
    if (palette === this._pending.palette && !this._error) return true;
    this._pending.palette = palette; this._error = ""; this.renderModal(); this.paintToolbar();
    this.shadowRoot.querySelector("[data-selected-style]")?.focus(); return true;
  }
  confirmSelectedStyle() {
    if (!this.selectedStyleReady()) { this._error = this.t(this.selectedStyleCurrent() ? "styleInvalid" : "styleChanged"); this.paintFeedback(); this.paintToolbar(); return false; }
    const {cards,palette} = this._pending, ids = new Set(cards.map(card => card.id)), count = cards.filter(card => card.palette !== palette).length;
    const change = layout => layout.cards.forEach(card => { if (ids.has(card.id)) card.palette = palette; });
    if (count && (!this.selectionCandidate(change) || !this.selectedStyleReady() || this._pending.palette !== palette)) return false;
    this._pending = null;
    const changed = count ? this.mutate(change) : false;
    if (count && !changed) return false;
    this._notice = this.t(count ? "styleApplied" : "styleNoChange").replace("{count}",count); this._error = "";
    this.renderModal(); this.paintToolbar(); this.paintFeedback(); this.announce(this._notice);
    this.shadowRoot.querySelector('[data-action="style-selected"]')?.focus(); return true;
  }
  requestSelectedDelete() {
    this.finishField(); if (!this.cardSelectionAllowed()) return false;
    const cards = this.selectionCards(); if (!cards?.length) return false;
    this._pending = {kind:"bulk-delete",scope:this.clipboardScope(),epoch:this._selectionEpoch,revision:this._saved.revision,version:this._draft.version,cards:AEH_CLONE(cards)};
    this.renderModal(); this.paintToolbar(); return true;
  }
  selectedDeleteCurrent() {
    const pending = this._pending;
    if (pending?.kind !== "bulk-delete" || !this.cardSelectionAllowed(true) || pending.scope !== this.clipboardScope() || pending.epoch !== this._selectionEpoch ||
        pending.revision !== this._saved.revision || pending.revision !== this.entry.layout.revision || pending.version !== this._draft.version) return false;
    const cards = this.selectionCards();
    return cards?.length === pending.cards.length && cards.every(card => pending.cards.some(prior => prior.id === card.id && JSON.stringify(prior) === JSON.stringify(card)));
  }
  confirmSelectedDelete() {
    if (!this.selectedDeleteCurrent()) { this._error = this.t("multiChanged"); this.renderModal(); this.paintFeedback(); this.paintToolbar(); return false; }
    const ids = new Set(this._pending.cards.map(card => card.id)), change = layout => { layout.cards = layout.cards.filter(card => !ids.has(card.id)); };
    if (!this.selectionCandidate(change)) return false;
    this._pending = null; this._selectedCardIds.clear();
    const changed = this.mutate(change);
    if (changed) { this._notice = this.t("multiDeleted").replace("{count}",ids.size); this.paintFeedback(); this.announce(this._notice); this.shadowRoot.querySelector('[data-action="selection-page"]')?.focus(); }
    return changed;
  }
  cardSelectionMarkup() {
    const blocked = this._busy || !!this._pending || !!this._drag || !!this._carry || this._conflict || this._profileStale || this.clipboardDisconnected() || !!Object.keys(this._fieldErrors).length;
    if (!this._selectingCards) return `<button class="text-button" data-action="selection-start" ${blocked ? "disabled" : ""}>${this.icon("mdi:checkbox-multiple-outline")}${this.t("multiStart")}</button>`;
    const cards = this.selectionCards() || [], disabled = blocked || this._conflict || !cards.length;
    const count = this.t("multiCount").replace("{count}",cards.length).replace("{page}",cards.filter(card => this.slotAt(card.slot)?.page_id === this._pageId).length);
    return `<div class="selection-tools" role="group" aria-label="${this.t("multiActive")}"><strong data-selection-count>${count}</strong><p>${this.t("multiHint")}</p><div><button data-action="selection-page" ${blocked || this._conflict ? "disabled" : ""}>${this.t("multiPage")}</button><button data-action="selection-clear" ${disabled ? "disabled" : ""}>${this.t("multiClear")}</button><button data-action="selection-exit" ${this._busy ? "disabled" : ""}>${this.t("multiDone")}</button></div><div><button data-action="copy-selected" ${disabled ? "disabled" : ""}>${this.t("groupCopy")}</button><button data-action="cut-selected" ${disabled ? "disabled" : ""}>${this.t("groupCut")}</button><button data-action="batch-show" ${disabled ? "disabled" : ""}>${this.t("multiShow")}</button><button data-action="batch-hide" ${disabled ? "disabled" : ""}>${this.t("multiHide")}</button><button data-action="style-selected" ${disabled || !this.stylePalettes().length ? "disabled" : ""}>${this.t("selectedStyle")}</button><button class="danger" data-action="batch-delete" ${disabled ? "disabled" : ""}>${this.t("multiDelete")}</button></div><p>${this.t("multiKeyboard")}</p></div>`;
  }
  paintCardSelection() { this.paintMarkup("#card-selection",this.cardSelectionMarkup()); }
  clipboardScope() {
    // A profile is a trusted editor definition, not negotiated firmware state.
    return JSON.stringify([this._hass?.user?.id ?? null,this._entryId,this.profile]);
  }
  clipboardDisconnected() {
    return !this.isConnected || this._hass?.connected === false || this._hass?.connection?.connected === false;
  }
  resetClipboardIntent() {
    this._cardClipboard = null; if (this._pending?.kind === "group-paste") this._pending = null;
  }
  clipboardIntent() {
    if (this.clipboardDisconnected() || this._cardClipboard?.scope !== this.clipboardScope() || (["group-copy","group-cut"].includes(this._cardClipboard?.mode) && this._profileStale)) {
      this.resetClipboardIntent();
    }
    return this._cardClipboard;
  }
  clipboardCard() {
    const intent = this.clipboardIntent();
    return intent?.mode === "copy" || intent?.mode === "cut" ? intent.card : undefined;
  }
  clipboardGroup() {
    const intent = this._cardClipboard;
    return ["group-copy","group-cut"].includes(intent?.mode) && intent.scope === this.clipboardScope() && !this.clipboardDisconnected() && !this._profileStale &&
      Array.isArray(intent.cards) && intent.cards.length > 0 && intent.cards.length <= 14 ? intent.cards : undefined;
  }
  copySelectedCards() { return this.captureSelectedGroup(false); }
  cutSelectedCards() { return this.captureSelectedGroup(true); }
  captureSelectedGroup(moving) {
    this.finishField(); if (!this.cardSelectionAllowed()) return false;
    if (moving && (!Number.isSafeInteger(this._saved?.revision) || this._saved.revision < 0 || this.entry.layout.revision !== this._saved.revision || ![2,3].includes(this._draft.version))) return false;
    const cards = this.selectionCards(); if (!cards?.length) return false;
    if (moving && cards.some(card => this._draft.cards.filter(item => item.slot === card.slot).length !== 1)) return false;
    const pages = this.pages.map(page => page.id);
    const snapshot = AEH_CLONE(cards).sort((a,b) => pages.indexOf(this.slotAt(a.slot).page_id)-pages.indexOf(this.slotAt(b.slot).page_id) || a.slot-b.slot);
    if (new TextEncoder().encode(JSON.stringify(snapshot)).length > this.draftLimit()) return false;
    this.resetCardSelection(); this._cardClipboard = {mode:moving ? "group-cut" : "group-copy",scope:this.clipboardScope(),cards:snapshot,
      ...(moving ? {epoch:this._selectionEpoch,revision:this._saved.revision,version:this._draft.version} : {})};
    this._notice = this.t(moving ? "groupCutReady" : "groupCopied").replace("{count}",snapshot.length); this._error = "";
    this.paintPreview(); this.paintClipboard(); this.paintInspector(); this.paintToolbar(); this.paintFeedback(); this.announce(this._notice);
    this.shadowRoot.querySelector('[data-action="paste-group"]')?.focus(); return true;
  }
  groupCutSourceSlots() {
    const intent = this._cardClipboard, cards = this.clipboardGroup();
    if (intent?.mode !== "group-cut" || !cards || !this._draft || !Array.isArray(this._draft.cards) || intent.epoch !== this._selectionEpoch || intent.revision !== this._saved?.revision ||
        intent.revision !== this.entry.layout.revision || intent.version !== this._draft.version || new Set(cards.map(card => card.id)).size !== cards.length || new Set(cards.map(card => card.slot)).size !== cards.length) return null;
    for (const prior of cards) {
      const matches = this._draft.cards.filter(card => card.id === prior.id), place = this.slotAt(prior.slot);
      if (matches.length !== 1 || !place || !this.acceptsCard(place,prior) || this._draft.cards.filter(card => card.slot === prior.slot).length !== 1 || JSON.stringify(matches[0]) !== JSON.stringify(prior)) return null;
    }
    return new Set(cards.map(card => card.slot));
  }
  canReviewGroupPaste(ownReview=false) {
    return !!this.clipboardGroup() && (this._cardClipboard.mode !== "group-cut" || !!this.groupCutSourceSlots()) && !!this._draft && !this._selectingCards && !this._busy && !this._drag && !this._carry && !this._conflict &&
      (!this._pending || (ownReview && this._pending.kind === "group-paste")) && !Object.keys(this._fieldErrors).length &&
      Number.isSafeInteger(this._saved?.revision) && this._saved.revision >= 0 && this.entry?.layout?.revision === this._saved.revision && [2,3].includes(this._draft.version);
  }
  requestGroupPaste() {
    this.finishField();
    if (this._cardClipboard?.mode === "group-cut" && !this.groupCutSourceSlots()) { this._error = this.t("groupCutChanged"); this.paintFeedback(); this.paintClipboard(); return false; }
    if (!this.canReviewGroupPaste()) return false;
    this._pending = {kind:"group-paste",scope:this.clipboardScope(),epoch:this._selectionEpoch,revision:this._saved.revision,version:this._draft.version,
      clipboard:this._cardClipboard,cards:AEH_CLONE(this.clipboardGroup()),targets:this.clipboardGroup().map(() => null)};
    this._error = ""; this.renderModal(); this.paintToolbar(); return true;
  }
  groupPasteCurrent() {
    const pending = this._pending;
    return pending?.kind === "group-paste" && this.canReviewGroupPaste(true) && pending.clipboard === this._cardClipboard &&
      pending.scope === this.clipboardScope() && pending.epoch === this._selectionEpoch && pending.revision === this._saved.revision &&
      pending.revision === this.entry.layout.revision && pending.version === this._draft.version &&
      JSON.stringify(pending.cards) === JSON.stringify(this._cardClipboard.cards) && Array.isArray(pending.targets) && pending.targets.length === pending.cards.length;
  }
  groupTargetCompatible(card,slot,cutSlots) {
    const place = Number.isInteger(slot) ? this.slotAt(slot) : null, moving = this._cardClipboard?.mode === "group-cut";
    const ownSlots = moving ? cutSlots === undefined ? this.groupCutSourceSlots() : cutSlots : null;
    return !!place && (!moving || !!ownSlots) && (!this.cardAt(slot) || !!ownSlots?.has(slot)) && this.acceptsCard(place,card) && (card.action?.kind !== "control" ||
      (this._draft.version === 3 && card.type === "entity" && ((card.action.control === "light" && card.entity_id.startsWith("light.")) || (card.action.control === "number" && card.entity_id.startsWith("input_number.")))));
  }
  groupPasteReady() {
    if (!this.groupPasteCurrent()) return false;
    const {cards,targets} = this._pending, moving = this._cardClipboard.mode === "group-cut", cutSlots = moving ? this.groupCutSourceSlots() : null;
    return this._draft.cards.length+(moving ? 0 : cards.length) <= this.profile.max_cards && new Set(targets).size === cards.length &&
      cards.every((card,index) => this.groupTargetCompatible(card,targets[index],cutSlots));
  }
  setGroupTarget(index,value) {
    if (!this.groupPasteCurrent() || !Number.isInteger(index) || index < 0 || index >= this._pending.cards.length) return false;
    const slot = value === "" ? null : /^(0|[1-9][0-9]*)$/.test(value) ? Number(value) : NaN;
    if (slot !== null && (!this.groupTargetCompatible(this._pending.cards[index],slot) || this._pending.targets.some((target,row) => row !== index && target === slot))) {
      this._error = this.t(this._cardClipboard?.mode === "group-cut" ? "groupMoveInvalid" : "groupInvalid"); this.renderModal(); this.paintToolbar(); this.shadowRoot.querySelector(`[data-group-target="${index}"]`)?.focus(); return false;
    }
    this._pending.targets[index] = slot; this._error = ""; this.renderModal(); this.paintToolbar();
    this.shadowRoot.querySelector(`[data-group-target="${index}"]`)?.focus(); return true;
  }
  groupTargetOptions(card,index) {
    const selected = this._pending.targets[index], used = new Set(this._pending.targets.filter((_,row) => row !== index));
    const cutSlots = this._cardClipboard?.mode === "group-cut" ? this.groupCutSourceSlots() : null;
    const stale = selected !== null && !this.groupTargetCompatible(card,selected,cutSlots);
    return `<option value="" ${selected === null ? "selected" : ""}>${this.t("groupChoose")}</option>${stale ? `<option value="${Number.isInteger(selected) ? selected : ""}" selected disabled>${this.t("groupUnavailable")}</option>` : ""}`+
      this.pages.map(page => `<optgroup label="${AEH_ESCAPE(this.pageTitle(page))}">${this.slots.filter(slot => slot.page_id === page.id && this.groupTargetCompatible(card,slot.slot,cutSlots)).sort((a,b) => a.slot-b.slot).map(slot => `<option value="${slot.slot}" ${slot.slot === selected ? "selected" : ""} ${used.has(slot.slot) ? "disabled" : ""}>${AEH_ESCAPE(this.pageTitle(page))} · ${this.t("slot")} ${slot.slot+1}</option>`).join("")}</optgroup>`).join("");
  }
  confirmGroupPaste() {
    if (!this.groupPasteReady()) {
      const moving = this._cardClipboard?.mode === "group-cut";
      this._error = this.t(moving && !this.groupCutSourceSlots() ? "groupCutChanged" : this.groupPasteCurrent() ? moving ? "groupMoveInvalid" : "groupInvalid" : "groupChanged");
      this.paintFeedback(); this.paintToolbar(); return false;
    }
    if (this._cardClipboard.mode === "group-cut") {
      const {cards,targets} = this._pending, mapping = new Map(cards.map((card,index) => [card.id,targets[index]]));
      const change = layout => layout.cards.forEach(card => { if (mapping.has(card.id)) card.slot = mapping.get(card.id); });
      if (!this.selectionCandidate(change) || !this.groupPasteReady()) return false;
      const unchanged = cards.every((card,index) => card.slot === targets[index]), first = this.slotAt(targets[0]);
      const changed = unchanged ? false : this.mutate(change);
      if (!unchanged && !changed) return false;
      this.resetClipboardIntent(); this._selectedSlot = first.slot; this._pageId = first.page_id;
      this._notice = this.t(unchanged ? "groupAlreadyThere" : "groupMoved").replace("{count}",cards.length); this._error = "";
      this.paintPages(); this.paintPreview(); this.renderModal(); this.paintClipboard(); this.paintInspector(); this.paintToolbar(); this.paintFeedback(); this.announce(this._notice); this.focusSlot(first.slot);
      return unchanged || changed;
    }
    const {cards,targets} = this._pending, used = new Set([...this._draft.cards.map(card => card.id),...cards.map(card => card.id)]), pasted = [];
    try {
      for (let index=0;index<cards.length;index++) {
        const id = `card-${AEH_UUID()}`;
        if (!/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(id) || used.has(id)) throw new Error("ID collision");
        used.add(id); pasted.push({...AEH_CLONE(cards[index]),id,slot:targets[index]});
      }
    } catch (_error) { this._error = this.t("groupIDs"); this.paintFeedback(); return false; }
    if (!this.groupPasteReady()) return false;
    if (!this.selectionCandidate(layout => { layout.cards.push(...pasted); })) return false;
    const first = this.slotAt(pasted[0].slot); this._pending = null; this._selectedSlot = first.slot; this._pageId = first.page_id;
    const changed = this.mutate(layout => { layout.cards.push(...pasted); });
    if (changed) { this._notice = this.t("groupPasted").replace("{count}",pasted.length); this.paintFeedback(); this.announce(this._notice); this.focusSlot(first.slot); }
    return changed;
  }
  cutSource() {
    const card = this.clipboardCard();
    if (!card || this._cardClipboard.mode !== "cut" || this._profileStale) return undefined;
    const source = this.cardAt(card.slot), place = this.slotAt(card.slot);
    return source && place && this.acceptsCard(place,source) && source.id === card.id &&
      this._draft.cards.filter(item => item.id === card.id).length === 1 && JSON.stringify(source) === JSON.stringify(card) ? source : undefined;
  }
  cutCard(slot=this._selectedSlot) {
    if (this._selectingCards || this.clipboardDisconnected() || this._profileStale || this._busy || this._pending || this._drag || this._carry) return false;
    this.finishField();
    const card = this.cardAt(slot), place = this.slotAt(slot);
    if (!card || !place || !this.acceptsCard(place,card) || Object.keys(this._fieldErrors).length ||
        new TextEncoder().encode(JSON.stringify(card)).length > this.draftLimit()) return false;
    this._cardClipboard = {mode:"cut",scope:this.clipboardScope(),card:AEH_CLONE(card)};
    this._notice = this.t("cutReady"); this.paintFeedback(); this.paintClipboard(); this.paintInspector(); this.paintToolbar();
    this.announce(this._notice); return true;
  }
  copyCard(slot=this._selectedSlot) {
    if (this._selectingCards || this.clipboardDisconnected() || this._busy || this._pending || this._drag || this._carry) return false;
    this.finishField();
    const card = this.cardAt(slot), place = this.slotAt(slot);
    if (!card || !place || !this.acceptsCard(place,card) || Object.keys(this._fieldErrors).length) return false;
    this._cardClipboard = {mode:"copy",scope:this.clipboardScope(),card:AEH_CLONE(card)};
    this._notice = this.t("copied"); this.paintFeedback(); this.paintClipboard(); this.paintInspector(); this.paintToolbar();
    this.announce(this._notice); return true;
  }
  canPasteCard(slot=this._selectedSlot) {
    const card = this.clipboardCard(), target = this.slotAt(slot);
    return !!card && !!target && !!this._draft && !this._selectingCards && !this._busy && !this._pending && !this._drag && !this._carry &&
      !Object.keys(this._fieldErrors).length && !this.cardAt(slot) && this.acceptsCard(target,card) &&
      (card.action?.kind !== "control" || this._draft.version === 3) &&
      (this._cardClipboard.mode === "cut" ? !!this.cutSource() : this._draft.cards.length < this.profile.max_cards);
  }
  pasteCard(slot=this._selectedSlot) {
    if (this._selectingCards) return false;
    if (this._busy || this._pending || this._drag || this._carry) return false;
    this.finishField();
    if (!this.canPasteCard(slot)) { this.announce(this.t(this._cardClipboard?.mode === "cut" ? (!this.cutSource() ? "cutChanged" : "movePasteEmpty") : "pasteEmpty")); return false; }
    const card = AEH_CLONE(this.clipboardCard()), target = this.slotAt(slot);
    if (this._cardClipboard.mode === "cut") {
      const source = this.cutSource(); if (!source) return false;
      const candidate = AEH_CLONE(this._draft);
      candidate.cards.find(item => item.id === source.id && item.slot === source.slot).slot = target.slot;
      if (new TextEncoder().encode(JSON.stringify(candidate)).length > this.draftLimit()) {
        this._error = this.t("tooLarge"); this.paintFeedback(); return false;
      }
      const changed = this.moveCard(source.slot,target.slot);
      if (changed) {
        this._cardClipboard = null; this._notice = this.t("pasteMoved");
        this.paintClipboard(); this.paintInspector(); this.paintToolbar(); this.paintFeedback(); this.announce(this._notice); this.focusSlot(target.slot);
      }
      return changed;
    }
    // Bound collision handling as well as document size. A copy never reuses
    // its source identity, including after an undo followed by another paste.
    let id;
    for (let attempt=0;attempt<3;attempt++) {
      const candidate = `card-${AEH_UUID()}`;
      if (candidate !== card.id && !this._draft.cards.some(item => item.id === candidate)) { id = candidate; break; }
    }
    if (!id) return false;
    card.id = id; card.slot = target.slot;
    const candidate = {...this._draft,cards:[...this._draft.cards,card]};
    if (new TextEncoder().encode(JSON.stringify(candidate)).length > this.draftLimit()) {
      this._error = this.t("tooLarge"); this.paintFeedback(); return false;
    }
    this._selectedSlot = target.slot; this._pageId = target.page_id;
    const changed = this.mutate(layout => { layout.cards.push(card); });
    if (changed) {
      this._notice = this.t("pasted"); this.paintFeedback(); this.announce(this._notice); this.focusSlot(target.slot);
    }
    return changed;
  }
  clearCardClipboard() {
    const moving = ["cut","group-cut"].includes(this._cardClipboard?.mode);
    const group = this._pending?.kind === "group-paste"; this.resetClipboardIntent(); if (group) this.renderModal();
    this._notice = this.t(moving ? "cutCleared" : "copyCleared");
    this.paintClipboard();
    if (!this.shadowRoot.querySelector("#inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
    this.paintToolbar(); this.paintFeedback(); this.announce(this._notice);
  }
  clipboardMarkup() {
    const intent = this.clipboardIntent(), group = this.clipboardGroup();
    if (group) {
      const moving = intent.mode === "group-cut";
      return `<div class="clipboard-note" data-clipboard-mode="${intent.mode}"><div><strong>${this.t(moving ? "groupCutOf" : "groupOf")}: ${group.length}</strong><p>${this.t(moving ? this.groupCutSourceSlots() ? "groupCutHint" : "groupCutChanged" : "groupHint")}</p></div><button class="tonal" data-action="paste-group" ${this.canReviewGroupPaste() ? "" : "disabled"}>${this.t(moving ? "groupMove" : "groupPaste")}</button><button class="text-button" data-action="clear-copy">${this.t(moving ? "clearCut" : "clearCopy")}</button></div>`;
    }
    const card = intent?.card;
    const moving = this._cardClipboard?.mode === "cut";
    return card ? `<div class="clipboard-note" data-clipboard-mode="${moving ? "cut" : "copy"}"><div><strong>${this.t(moving ? "cutOf" : "copyOf")}: ${AEH_ESCAPE(card.title)}</strong><p>${this.t(moving ? (this.cutSource() ? "cutHint" : "cutChanged") : "copyHint")}</p></div><button class="text-button" data-action="clear-copy">${this.icon("mdi:close")}${this.t(moving ? "clearCut" : "clearCopy")}</button></div>` : "";
  }
  pasteMarkup(slot=this._selectedSlot) {
    if (!this.clipboardCard()) return "";
    const moving = this._cardClipboard?.mode === "cut";
    return `<button class="tonal" type="button" data-action="paste-card" ${this.canPasteCard(slot) ? "" : "disabled"} title="${this.t(moving ? "movePasteEmpty" : "pasteEmpty")}">${this.icon("mdi:content-paste")}${this.t(moving ? "pasteMove" : "paste")}</button>`;
  }

  async save() {
    this.finishField();
    const form = this.shadowRoot.querySelector("#properties");
    if (this._busy || !this.dirty || this._conflict || Object.keys(this._fieldErrors).length || (form && !form.reportValidity())) return false;
    if (!this.sunLayoutAllowed(this._draft)) return this.refuseSunPlacement();
    const id = this._entryId, epoch = this._selectionEpoch, revision = this._saved.revision, layout = AEH_CLONE(this._draft);
    this._statusRequest++; this._busy = true; this._error = ""; this.paintToolbar();
    try {
      const result = await this.ws("layout/save",{entry_id:id,expected_revision:revision,layout});
      if (id !== this._entryId || epoch !== this._selectionEpoch) return false;
      this.resetCardSelection(); this._saved = AEH_CLONE(result.layout); this._draft = AEH_CLONE(result.layout);
      this.entry.layout = AEH_CLONE(result.layout); this._status = {...result.status}; this._statusError = false;
      this._undo = []; this._redo = []; this._notice = this.t("savedNotice"); this._conflict = false;
      this._restoreConflict = false; this._draftBaseRevision = result.layout.revision; this._recovery = null; this.clearStoredDraft();
      this.render(); return true;
    } catch (error) {
      if (id !== this._entryId || epoch !== this._selectionEpoch) return false;
      if (error?.code === "revision_conflict" || error?.error?.code === "revision_conflict") this._conflict = true;
      this._error = `${this.t("saveFailed")}: ${this.errorText(error)}`; this.paintFeedback(); return false;
    } finally { if (epoch === this._selectionEpoch) { this._busy = false; this.paintToolbar(); } }
  }
  async reloadSaved() {
    const id = this._entryId, epoch = this._selectionEpoch; this._statusRequest++; this._busy = true; this.paintToolbar();
    try {
      const result = await this.ws("layout/get",{entry_id:id}); if (id !== this._entryId || epoch !== this._selectionEpoch) return;
      const latest = result.entries[0]; if (!latest) return;
      if (this.dirty) { this._recovery = AEH_CLONE(this._draft); this._recoveryBaseRevision = this._draftBaseRevision; this.persistDraft(); }
      this.resetCardSelection(); Object.assign(this.entry,latest); this._saved = AEH_CLONE(latest.layout); this._draft = AEH_CLONE(latest.layout);
      this._status = {...latest.status}; this._statusError = false; this._profileStale = false; this._undo = []; this._redo = []; this._conflict = false;
      this._restoreConflict = false; this._draftBaseRevision = latest.layout.revision;
      this._notice = this._recovery ? this.t("recovered") : this.t("clean"); this._error = ""; this._fieldErrors = {};
      this.render();
    } catch (error) {
      if (id !== this._entryId || epoch !== this._selectionEpoch) return;
      this._error = `${this.t("reloadFailed")}: ${this.errorText(error)}`; this.paintFeedback();
    }
    finally { if (epoch === this._selectionEpoch) { this._busy = false; this.paintToolbar(); } }
  }
  restoreDraft() {
    if (!this._recovery) return;
    this._statusRequest++;
    const recovery = AEH_CLONE(this._recovery); recovery.revision = this._saved.revision;
    const base = this._recoveryBaseRevision ?? this._saved.revision;
    this.resetCardSelection(); this.mutate(() => { this._draft = recovery; }); this._recovery = null;
    this._draftBaseRevision = base; this._restoreConflict = base !== this._saved.revision && this.dirty; this._conflict = this._restoreConflict;
    this._notice = this.t("restored"); this.paintFeedback();
  }
  async exportSaved() {
    if (this._busy) return;
    const id = this._entryId, title = this.entry.title;
    try {
      const result = await this.ws("layout/export",{entry_id:id});
      if (id !== this._entryId) return;
      const blob = new Blob([JSON.stringify(result.backup,null,2)],{type:"application/json"});
      const url = URL.createObjectURL(blob), link = document.createElement("a");
      link.href = url; link.download = `atmosfera-${(title || "screen").replace(/[^a-z0-9_-]/gi,"-")}.json`;
      link.hidden = true; document.body.append(link); link.click(); link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url),1000);
      this._notice = this.t("exportHint"); this._error = ""; this.paintFeedback();
    } catch (error) { this._error = this.errorText(error); this.paintFeedback(); }
  }
  async importText(text) {
    if (this._selectingCards) return false;
    if (new TextEncoder().encode(text).length > (this.profile?.max_document_bytes || 32768)) throw new Error(this.t("tooLarge"));
    let backup;
    try { backup = JSON.parse(text); } catch (_ignored) { throw new Error(this.t("invalidFile")); }
    if (!backup || backup.format !== "atmosfera-layout" || backup.version !== 1) throw new Error(this.t("unsupported"));
    if (!this.sunLayoutAllowed(backup.layout)) throw new Error(this.t("sunPlacement"));
    this._statusRequest++;
    const id = this._entryId, epoch = this._selectionEpoch, revision = this._saved.revision;
    const result = await this.ws("layout/import",{entry_id:id,expected_revision:revision,backup,dry_run:true});
    if (id !== this._entryId || epoch !== this._selectionEpoch || revision !== this._saved.revision) return false;
    if (!this.sunLayoutAllowed(result.layout)) throw new Error(this.t("sunPlacement"));
    this._pending = {kind:"import",layout:result.layout,warnings:result.warnings || []}; this.renderModal(); return true;
  }
  useImported() {
    if (this._pending?.kind !== "import") return;
    if (!this.sunLayoutAllowed(this._pending.layout)) { this.refuseSunPlacement(); return; }
    this._statusRequest++;
    const imported = AEH_CLONE(this._pending.layout); imported.revision = this._saved.revision;
    this.resetCardSelection(); this._pending = null; this.mutate(() => { this._draft = imported; });
    this._notice = this.t("imported"); this.render();
  }
  finishField() {
    if (!this._fieldBefore) return;
    this.pushHistory(this._fieldBefore); this._fieldBefore = null; this.paintToolbar(); this.paintFeedback();
  }
  lightControlAvailability(card=this.cardAt(this._selectedSlot)) {
    if (this._profileStale) return {ready:false,reason:"controlProfileChanged",brightness:false};
    const supported = this.isConnected && !this._statusError && !this._profileStale && this._status.device_available === true
      && this._status.light_control_status === "ready" && Array.isArray(this._status.native_control_types)
      && (this._status.native_control_types.includes("light_brightness_v1") || (this._status.native_control_types.includes("entity_control_v1") && this._status.entity_control_status === "ready" && Array.isArray(this._status.control_kinds) && this._status.control_kinds.includes("light")))
      && Array.isArray(this.profile?.layout_versions) && this.profile.layout_versions.includes(3)
      && Array.isArray(this.profile?.schema_control_types) && this.profile.schema_control_types.includes("light");
    if (!supported) return {ready:false,reason:"controlUnsupported",brightness:false};
    const slot = this.slotAt(card?.slot), entity = this.entityFor(card?.entity_id), state = this._hass?.states?.[card?.entity_id];
    const actions = Array.isArray(entity?.actions) ? entity.actions : [];
    const turnOn = actions.find(action => action.service === "light.turn_on"), turnOff = actions.some(action => action.service === "light.turn_off");
    if (!card || card.type !== "entity" || !card.visible || !slot || !card.entity_id.startsWith("light.") || entity?.domain !== "light" || entity.available !== true || !["on","off"].includes(entity.state) || !["on","off"].includes(state?.state) || (!turnOn && !turnOff)) return {ready:false,reason:"controlEntity",brightness:false};
    const modes = state.attributes?.supported_color_modes;
    const brightness = !!turnOn && turnOff && !!turnOn.fields?.brightness_pct && Array.isArray(modes)
      && modes.every(mode => typeof mode === "string") && modes.some(mode => ["brightness","color_temp","hs","xy","rgb","rgbw","rgbww","white"].includes(mode));
    return {ready:true,reason:brightness ? "controlBrightness" : "controlPowerOnly",brightness,caps:{turn_on:!!turnOn,turn_off:turnOff,brightness}};
  }
  numberControlAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported = {ready:false,reason:this._profileStale ? "controlProfileChanged" : "numberUnsupported"};
    if (!this.isConnected || this._statusError || this._profileStale || this._status.device_available !== true
      || this._status.entity_control_status !== "ready" || !Array.isArray(this._status.native_control_types) || !this._status.native_control_types.includes("entity_control_v1")
      || !Array.isArray(this._status.control_kinds) || !this._status.control_kinds.includes("number")
      || !Array.isArray(this.profile?.layout_versions) || !this.profile.layout_versions.includes(3)
      || !Array.isArray(this.profile?.schema_control_types) || !this.profile.schema_control_types.includes("number")) return unsupported;
    const slot = this.slotAt(card?.slot), entity = this.entityFor(card?.entity_id), state = this._hass?.states?.[card?.entity_id];
    const descriptor = entity?.number_control?.domain, attrs = state?.attributes;
    const actions = Array.isArray(entity?.actions) ? entity.actions : [];
    const action = actions.find(item => item && typeof item === "object" && item.service === "input_number.set_value");
    if (!card || card.type !== "entity" || !card.visible || !slot?.editable || slot.hidden
      || !card.entity_id.startsWith("input_number.") || entity?.domain !== "input_number" || entity.available !== true
      || !state || ["unknown","unavailable"].includes(state.state) || !action || !descriptor || descriptor.schema !== "numeric_steps_v1"
      || !Number.isInteger(entity.number_control.index) || !attrs) return {ready:false,reason:"numberEntity"};
    // Server metadata is canonical and bounded by NumericDomain. This fingerprint
    // only detects a changed review; backend dispatch revalidates authoritative data.
    return {ready:true,reason:"numberHint",caps:{domain:descriptor,metadata:{min:attrs.min,max:attrs.max,step:attrs.step,unit:attrs.unit_of_measurement ?? ""}}};
  }
  controlAvailability(card,kind="light") {
    return kind === "number" ? this.numberControlAvailability(card) : this.lightControlAvailability(card);
  }
  controlText(key,kind="light") {
    const number = {control:"numberControl",controlReviewTitle:"numberReviewTitle",controlReviewV2:"numberReviewV2",controlReviewV3:"numberReviewV3",controlConfirm:"numberConfirm",controlNotice:"numberNotice"};
    return this.t(kind === "number" && number[key] ? number[key] : key);
  }
  paintControlAvailability() {
    // Do not replace a field under the user's cursor. Admission is rechecked
    // on selection and confirmation, including when a displayed option is old.
    if (!this.shadowRoot.querySelector(".inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
    if (this._pending?.kind === "light-control") this.renderModal();
  }
  requestLightControl(controlKind="light") {
    if (this._selectingCards) return false;
    this.finishField();
    const card = this.cardAt(this._selectedSlot);
    if (this._busy || this._pending || this._conflict || this._drag || this._carry || Object.keys(this._fieldErrors).length || ![2,3].includes(this._draft?.version) || !["light","number"].includes(controlKind) || !this.controlAvailability(card,controlKind).ready) { this.paintInspector(); return false; }
    if (card.action.kind === "control" && card.action.control === controlKind) return false;
    this._pending = {kind:"light-control",controlKind,entryId:this._entryId,epoch:this._selectionEpoch,user:this._hass?.user?.id,
      cardId:card.id,slot:card.slot,savedRevision:this._saved?.revision,draftRevision:this._draft.revision,layout:AEH_COMPARE(this._draft),profile:JSON.stringify(this.profile),caps:JSON.stringify(this.controlAvailability(card,controlKind).caps)};
    this.paintInspector(); this.renderModal(); return true;
  }
  confirmLightControl() {
    const pending = this._pending, card = this.cardAt(pending?.slot);
    if (pending?.kind !== "light-control" || this._busy) return false;
    if (!this.lightControlReviewCurrent()) {
      this._pending = null; this._error = this.t("controlChanged"); this.paintInspector(); this.renderModal(); this.paintFeedback(); return false;
    }
    this._pending = null;
    const controlKind = pending.controlKind || "light";
    const changed = this.mutate(layout => { layout.version = 3; card.action = {kind:"control",control:controlKind}; });
    if (changed) { this._notice = this.controlText("controlNotice",controlKind); this.paintFeedback(); }
    return changed;
  }
  lightControlReviewCurrent() {
    const pending = this._pending, card = this.cardAt(pending?.slot);
    return pending?.kind === "light-control" && !this._conflict && pending.entryId === this._entryId && pending.epoch === this._selectionEpoch
      && pending.user === this._hass?.user?.id && pending.cardId === card?.id && pending.layout === AEH_COMPARE(this._draft)
      && pending.savedRevision === this._saved?.revision && pending.draftRevision === this._draft?.revision
      && pending.profile === JSON.stringify(this.profile) && pending.caps === JSON.stringify(this.controlAvailability(card,pending.controlKind || "light").caps) && this.controlAvailability(card,pending.controlKind || "light").ready;
  }
  parseFieldValue(input, descriptor) {
    const value = input.value;
    if (value === "") { if (descriptor.required) throw new Error(this.t("requiredValue")); return undefined; }
    if (descriptor.type === "number") {
      const number = Number(value);
      if (!Number.isFinite(number) || (descriptor.min !== undefined && number < descriptor.min) || (descriptor.max !== undefined && number > descriptor.max)) throw new Error(this.t("checkNumber"));
      return number;
    }
    if (descriptor.type === "rgb") {
      const channels = value.split(",").map(part => Number(part.trim()));
      if (channels.length !== 3 || value.split(",").some(part => !part.trim()) || channels.some(number => !Number.isInteger(number) || number < 0 || number > 255)) throw new Error(this.t("checkRgb"));
      return channels;
    }
    if (descriptor.type === "boolean") {
      if (!["true","false"].includes(value)) throw new Error(this.t("requiredValue"));
      return value === "true";
    }
    if (descriptor.type === "select" && !descriptor.options.includes(value)) throw new Error(this.t("requiredValue"));
    return value;
  }
  editField(input) {
    if (this._selectingCards) return;
    if (this._busy) return;
    const card = this.cardAt(this._selectedSlot); if (!card) return;
    if (input.dataset.field === "action-kind" && ["control","control-number"].includes(input.value)) { this.requestLightControl(input.value === "control-number" ? "number" : "light"); return; }
    if (!this._fieldBefore) this._fieldBefore = AEH_CLONE(this._draft);
    const field = input.dataset.field;
    try {
      if (field === "visible") card.visible = input.checked;
      else if (field === "type") { card.type = input.value; if (card.type === "sensor" || (card.type !== "entity" && card.action.kind === "control")) card.action = {kind:"none"}; }
      else if (field === "action-kind") {
        card.action = input.value === "service" ? {kind:"service",service:"",data:{}} : {kind:input.value};
      } else if (field === "service") card.action = {kind:"service",service:input.value,data:{}};
      else if (field.startsWith("data:")) {
        const key = field.slice(5), action = this.entityFor(card.entity_id)?.actions.find(item => item.service === card.action.service);
        const descriptor = action?.fields[key]; if (!descriptor) return;
        const value = this.parseFieldValue(input,descriptor);
        if (value === undefined) delete card.action.data[key]; else card.action.data[key] = value;
      } else card[field] = input.value;
      delete this._fieldErrors[field]; input.removeAttribute("aria-invalid");
    } catch (error) { this._fieldErrors[field] = this.errorText(error); input.setAttribute("aria-invalid","true"); }
    const error = this.shadowRoot.querySelector("[data-field-error]");
    if (error) error.textContent = Object.values(this._fieldErrors).join(" ");
    this.paintPreview(); if (["cut","group-cut"].includes(this._cardClipboard?.mode)) this.paintClipboard(); this.paintToolbar(); this.scheduleDraft();
  }

  onInput(event) {
    const input = event.target;
    if (input.id === "search") {
      this._query = input.value; window.clearTimeout(this._queryTimer);
      this._queryTimer = window.setTimeout(() => this.fetchCatalogue(),180);
    } else if (input.dataset?.field) this.editField(input);
  }
  async onChange(event) {
    const input = event.target;
    if (input.id === "device") return this.requestSwitch(input.value);
    if (input.id === "domain") { this._domain = input.value; return this.fetchCatalogue(); }
    if (input.id === "area") { this._area = input.value; return this.fetchCatalogue(); }
    if (input.dataset?.selectedStyle !== undefined) return this.setSelectedStyle(input.value);
    if (input.dataset?.groupTarget !== undefined) return this.setGroupTarget(Number(input.dataset.groupTarget),input.value);
    if (input.id === "move-target" && input.value !== "") { const from = this._selectedSlot; return this.moveCard(from,Number(input.value)); }
    if (input.id === "import-file") {
      const file = input.files?.[0]; input.value = "";
      if (!file) return;
      try {
        if (file.size > (this.profile?.max_document_bytes || 32768)) throw new Error(this.t("tooLarge"));
        await this.importText(await file.text());
      } catch (error) { this._error = this.errorText(error); this.paintFeedback(); }
    } else if (input.dataset?.field) {
      this.finishField();
      if (["type","action-kind","service"].includes(input.dataset.field)) this.paintInspector();
    }
  }
  async onClick(event) {
    if (Date.now() < this._suppressClickUntil) { event.preventDefault(); return; }
    const button = event.target.closest("[data-action]"); if (!button || button.disabled) return;
    const action = button.dataset.action;
    if (this._busy) return;
    if (action === "selection-start") return this.startCardSelection();
    if (action === "selection-exit") return this.endCardSelection();
    if (action === "selection-page") return this.selectPageCards();
    if (action === "selection-clear") return this.clearCardSelection();
    if (action === "copy-selected") return this.copySelectedCards();
    if (action === "cut-selected") return this.cutSelectedCards();
    if (action === "paste-group") return this.requestGroupPaste();
    if (action === "modal-paste-group") return this.confirmGroupPaste();
    if (action === "batch-show") return this.setSelectedVisibility(true);
    if (action === "batch-hide") return this.setSelectedVisibility(false);
    if (action === "style-selected") return this.requestSelectedStyle();
    if (action === "modal-style-selected") return this.confirmSelectedStyle();
    if (action === "batch-delete") return this.requestSelectedDelete();
    if (action === "modal-batch-delete") return this.confirmSelectedDelete();
    if (action === "save") return this.save();
    if (action === "undo" || action === "redo") return this.history(action);
    if (action === "slot") return this.selectSlot(button.dataset.slot);
    if (action === "entity") return this.assignEntity(button.dataset.entity);
    if (action === "page") { this.finishField(); this._pageId = button.dataset.page; this._selectedSlot = null; this.render(); return; }
    if (action === "remove") return this.removeCard();
    if (action === "copy-card") return this.copyCard();
    if (action === "cut-card") return this.cutCard();
    if (action === "paste-card") return this.pasteCard();
    if (action === "clear-copy") return this.clearCardClipboard();
    if (action === "close-inspector") { this.finishField(); this._selectedSlot = null; this.render(); return; }
    if (action === "focus-library") { this.shadowRoot.querySelector("#search")?.focus(); return; }
    if (action === "export") return this.exportSaved();
    if (action === "import") { if (!this._selectingCards) return this.shadowRoot.querySelector("#import-file")?.click(); return; }
    if (action === "reload") return this.reloadSaved();
    if (action === "restore") return this.restoreDraft();
    if (action === "review-draft") return this.reviewRestoredDraft();
    if (action === "modal-restore") return this.restoreStoredDraft();
    if (action === "modal-discard-draft") return this.discardStoredDraft();
    if (action === "retry") return this._data ? this.fetchCatalogue() : this.load();
    if (action === "modal-cancel") { const bulk = this._pending?.kind === "bulk-delete", group = this._pending?.kind === "group-paste", style = this._pending?.kind === "bulk-style"; this._pending = null; this.renderModal(); if (bulk || group || style) this.paintToolbar(); if (group || style) this.shadowRoot.querySelector(style ? '[data-action="style-selected"]' : '[data-action="paste-group"]')?.focus(); return; }
    if (action === "modal-import") return this.useImported();
    if (action === "modal-light-control") return this.confirmLightControl();
    if (action === "modal-discard") { const id = this._pending.entryId; this._draft = AEH_CLONE(this._saved); this._recovery = null; this.clearStoredDraft(); this._pending = null; return this.selectEntry(id); }
    if (action === "modal-save") {
      const id = this._pending.entryId; const saved = await this.save(); if (saved) this.selectEntry(id);
    }
  }

  onPointerDown(event) {
    const handle = event.target.closest("[data-drag-kind]");
    if (!handle || event.button !== 0 || this._selectingCards || this._busy || this._pending) return;
    this.finishField(); this._carry = null;
    this._drag = {kind:handle.dataset.dragKind,from:Number(handle.dataset.from),entity:handle.dataset.entity,pointer:event.pointerId,
      x:event.clientX,y:event.clientY,active:false,target:null};
    // Capture on the stable host: changing preview pages can remove the original touch handle.
    try { this.setPointerCapture?.(event.pointerId); } catch (_ignored) { /* Synthetic tests have no active pointer. */ }
    window.addEventListener("pointermove",this._pointerMove,{passive:false});
    window.addEventListener("pointerup",this._pointerUp);
    window.addEventListener("pointercancel",this._pointerCancel);
  }
  onPointerMove(event) {
    const drag = this._drag; if (!drag || event.pointerId !== drag.pointer) return;
    if (!drag.active && Math.hypot(event.clientX-drag.x,event.clientY-drag.y) < 7) return;
    event.preventDefault();
    if (!drag.active) {
      drag.active = true;
      this._ghost = document.createElement("div"); this._ghost.className = "drag-ghost";
      this._ghost.textContent = drag.kind === "card" ? this.cardAt(drag.from)?.title || this.t("entity") : this.entityFor(drag.entity)?.name || drag.entity;
      this.shadowRoot.append(this._ghost);
    }
    this._ghost.style.left = `${event.clientX+14}px`; this._ghost.style.top = `${event.clientY+14}px`;
    const under = this.shadowRoot.elementFromPoint(event.clientX,event.clientY);
    const page = under?.closest('[data-action="page"]');
    if (page && page.dataset.page !== this._pageId && !page.disabled) {
      if (drag.hoverPage !== page.dataset.page) {
        window.clearTimeout(drag.pageTimer); drag.hoverPage = page.dataset.page;
        drag.pageTimer = window.setTimeout(() => {
          if (this._drag !== drag) return;
          this._pageId = drag.hoverPage; this.paintPages(); this.paintPreview(); this._selectedSlot = null; this.paintInspector();
        },500);
      }
    } else { window.clearTimeout(drag.pageTimer); drag.hoverPage = null; }
    const slot = under?.closest("[data-slot].preview-card");
    drag.target = slot ? Number(slot.dataset.slot) : null; this.paintDropTarget(drag.target);
  }
  onPointerUp(event) {
    const drag = this._drag; if (!drag || event.pointerId !== drag.pointer) return;
    const active = drag.active, target = drag.target, kind = drag.kind, from = drag.from, entity = drag.entity;
    this.cancelMove(false);
    if (!active) return;
    this._suppressClickUntil = Date.now()+350;
    if (target !== null) kind === "card" ? this.moveCard(from,target) : this.assignEntity(entity,target);
    else this.announce(this.t("cancelled"));
  }
  cancelMove(speak=true) {
    if (this._drag?.pageTimer) window.clearTimeout(this._drag.pageTimer);
    const had = this._drag?.active || this._carry, pointer = this._drag?.pointer;
    if (pointer !== undefined && this.hasPointerCapture?.(pointer)) this.releasePointerCapture(pointer);
    this._drag = null; this._carry = null; this._ghost?.remove(); this._ghost = null;
    window.removeEventListener("pointermove",this._pointerMove);
    window.removeEventListener("pointerup",this._pointerUp);
    window.removeEventListener("pointercancel",this._pointerCancel);
    this.paintDropTarget(null); if (had && speak) this.announce(this.t("cancelled"));
  }
  startCarry(handle) {
    if (this._selectingCards) return false;
    this._carry = {kind:handle.dataset.dragKind,from:Number(handle.dataset.from),entity:handle.dataset.entity};
    const slot = this.slotAt(this._selectedSlot) || this.pageSlots[0]; if (slot) this.focusSlot(slot.slot);
    this.announce(this.t("picked")); this.paintDropTarget(slot?.slot);
  }
  onKeyDown(event) {
    const input = event.target;
    if (event.key === "Escape" && this._selectingCards) { event.preventDefault(); this.endCardSelection(); return; }
    if (event.key === "Escape" && this._cardClipboard) this.clearCardClipboard();
    if (this._pending) {
      if (this._busy) { event.preventDefault(); return; }
      if (event.key === "Escape") { event.preventDefault(); this._pending = null; this.renderModal(); }
      if (event.key === "Tab") {
        const buttons = [...this.shadowRoot.querySelectorAll(["group-paste","bulk-style"].includes(this._pending.kind) ? ".modal select:not([disabled]),.modal button:not([disabled])" : ".modal button:not([disabled])")];
        const index = buttons.indexOf(input);
        if (buttons.length && ((event.shiftKey && index <= 0) || (!event.shiftKey && index === buttons.length-1))) {
          event.preventDefault(); buttons[event.shiftKey ? buttons.length-1 : 0].focus();
        }
      }
      return;
    }
    if (this._busy) return;
    const field = ["INPUT","SELECT","TEXTAREA"].includes(input.tagName) || input.isContentEditable || !!input.closest('[contenteditable="true"]');
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") { event.preventDefault(); this.save(); return; }
    if ((event.ctrlKey || event.metaKey) && !field && ["z","y"].includes(event.key.toLowerCase())) {
      event.preventDefault(); this.history(event.shiftKey || event.key.toLowerCase() === "y" ? "redo" : "undo"); return;
    }
    if (event.key === "Escape") { this.cancelMove(); return; }
    if (field) return;
    const handle = input.closest("[data-drag-kind]");
    const tile = input.closest(".preview-card");
    if (this._selectingCards && tile && (event.key === "Enter" || event.code === "Space")) { event.preventDefault(); this.toggleCardSelection(Number(tile.dataset.slot)); return; }
    if (this._selectingCards && event.key === "Delete") { event.preventDefault(); this.requestSelectedDelete(); return; }
    if ((event.ctrlKey || event.metaKey) && !event.altKey && ["c","x","v"].includes(event.key.toLowerCase())) {
      event.preventDefault();
      const slot = tile ? Number(tile.dataset.slot) : this._selectedSlot;
      if (event.key.toLowerCase() === "c" && this._selectingCards) this.copySelectedCards();
      else if (event.key.toLowerCase() === "x" && this._selectingCards) this.cutSelectedCards();
      else if (event.key.toLowerCase() === "v" && this.clipboardGroup()) this.requestGroupPaste();
      else event.key.toLowerCase() === "c" ? this.copyCard(slot) : event.key.toLowerCase() === "x" ? this.cutCard(slot) : this.pasteCard(slot); return;
    }
    if (event.code === "Space" && (handle || (tile && this.cardAt(tile.dataset.slot)))) {
      event.preventDefault(); this.startCarry(handle || {dataset:{dragKind:"card",from:tile.dataset.slot}}); return;
    }
    if (tile && this._carry && event.key === "Enter") {
      event.preventDefault(); const carry = this._carry; this.cancelMove(false);
      carry.kind === "card" ? this.moveCard(carry.from,Number(tile.dataset.slot)) : this.assignEntity(carry.entity,Number(tile.dataset.slot)); return;
    }
    if (tile && !this._carry && (event.key === "Enter" || event.code === "Space")) {
      event.preventDefault(); this.selectSlot(Number(tile.dataset.slot)); return;
    }
    if (tile && ["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"].includes(event.key)) {
      event.preventDefault();
      const current = this.slotAt(tile.dataset.slot), horizontal = ["ArrowLeft","ArrowRight"].includes(event.key);
      const sign = ["ArrowLeft","ArrowUp"].includes(event.key) ? -1 : 1;
      const cx = current.x+current.width/2, cy = current.y+current.height/2;
      const candidates = this.pageSlots.filter(slot => slot !== current).map(slot => {
        const dx = slot.x+slot.width/2-cx, dy = slot.y+slot.height/2-cy;
        return {slot,forward:(horizontal ? dx : dy)*sign,score:Math.hypot(dx,dy)+(horizontal ? Math.abs(dy) : Math.abs(dx))*2};
      }).filter(item => item.forward > 5).sort((a,b) => a.score-b.score);
      if (candidates[0]) { this.focusSlot(candidates[0].slot.slot); if (this._carry) this.paintDropTarget(candidates[0].slot.slot); }
    } else if (tile && event.key === "Delete") { event.preventDefault(); this._selectedSlot = Number(tile.dataset.slot); this.removeCard(); }
  }
  focusSlot(slot) { this.shadowRoot.querySelector(`.preview-card[data-slot="${Number(slot)}"]`)?.focus(); }
  paintDropTarget(slot) {
    this.shadowRoot.querySelectorAll?.(".preview-card").forEach(card => card.classList.toggle("drop-target",slot !== null && Number(card.dataset.slot) === Number(slot)));
  }
  announce(message) { const live = this.shadowRoot.querySelector("#announcement"); if (live) live.textContent = message; }

  stateText(card) {
    if (!card?.entity_id) return this.t("noEntity");
    const state = this._hass?.states?.[card.entity_id], entity = this.entityFor(card.entity_id);
    if (!state) return entity?.state || this.t("unknown");
    if (state.state === "unavailable") return this.t("offline");
    if (typeof this._hass.formatEntityState === "function") {
      try { return this._hass.formatEntityState(state); } catch (_ignored) { /* Older HA frontends retain the raw fallback. */ }
    }
    const unit = state.attributes?.unit_of_measurement;
    return `${state.state}${unit ? ` ${unit}` : ""}`;
  }
  paletteColors(name) {
    const provided = this.entry?.colors?.[name];
    const rgb = value => Number.isInteger(value) && value >= 0 && value <= 0xFFFFFF;
    if (provided && rgb(provided.background) && rgb(provided.foreground)) return {background:this.hex(provided.background),foreground:this.hex(provided.foreground)};
    const raw = this.entry?.accent_color;
    const seed = typeof raw === "string" && /^[0-9a-f]{6}$/i.test(raw) ? parseInt(raw,16) : 0x36BCF0;
    const r = seed >> 16 & 255, g = seed >> 8 & 255, b = seed & 255;
    const roles = {primary:[r,g,b],secondary:[Math.min(255,r+28),Math.min(255,g+20),Math.min(255,b+10)],tertiary:[Math.min(255,r+8),Math.min(255,g+38),Math.min(255,b+38)],primary_container:[Math.min(255,r+58),Math.min(255,g+58),Math.min(255,b+58)],surface:[r/5|0,g/5|0,b/5|0]};
    const [red,green,blue] = Object.hasOwn(roles,name) ? roles[name] : roles.surface;
    return {background:this.hex((red<<16)|(green<<8)|blue),foreground:this.hex(red*299+green*587+blue*114 > 150000 ? 0x071018 : 0xFFFFFF)};
  }
  paintAppearance() {
    // Update only colors: preserve drag targets, active inputs and draft/history.
    for (const node of this.shadowRoot.querySelectorAll(".preview-card[data-slot]")) {
      const slot = Number(node.dataset.slot), card = Number.isInteger(slot) ? this.cardAt(slot) : null;
      const colors = this.paletteColors(card?.palette || "surface");
      node.style.setProperty("--tile-bg",colors.background); node.style.setProperty("--tile-fg",colors.foreground);
    }
    for (const node of this.shadowRoot.querySelectorAll(".palette-swatches [data-palette]")) node.style.background = this.paletteColors(node.dataset.palette).background;
  }
  hex(value) { return `#${(Number(value)&0xFFFFFF).toString(16).padStart(6,"0")}`; }
  pageTitle(page) { return page.id === "home-2" ? this.t("security") : page.id === "home-4" ? this.t("controls") : page.title; }
  pageMarkup() {
    if (!Array.isArray(this.profile?.pages)) return "";
    const editable = new Set(this.pages.map(page => page.id));
    return [...this.profile.pages].sort((a,b) => a.order-b.order).map(page => {
      if (editable.has(page.id)) return `<button class="page-tab ${page.id === this._pageId ? "active" : ""}" data-action="page" data-page="${AEH_ESCAPE(page.id)}" role="tab" aria-selected="${page.id === this._pageId}">${page.id === "home-2" ? this.icon("alarm") : this.icon("switch")}${AEH_ESCAPE(this.pageTitle(page))}</button>`;
      const title = page.id === "home-1" ? this.t("home") : page.id === "home-3" ? this.t("apps") : this.pageTitle(page) || page.id;
      const icon = page.id === "home-1" ? "mdi:weather-partly-cloudy" : page.id === "home-3" ? "mdi:apps" : "mdi:file-outline";
      return `<span class="reserved-page" title="${AEH_ESCAPE(page.id === "home-1" || page.id === "home-3" ? this.t("reserved") : title)}">${this.icon(icon)}${AEH_ESCAPE(title)}</span>`;
    }).join("");
  }
  previewMarkup() {
    const page = this.pages.find(item => item.id === this._pageId);
    const selecting = this._selectingCards;
    const cards = this.pageSlots.map(slot => {
      const card = this.cardAt(slot.slot), colors = this.paletteColors(card?.palette || "surface");
      const shape = slot.radius ?? Math.min(slot.width,slot.height)/2;
      const compact = slot.height <= 120, strip = slot.height < 90, sensor = slot.slot === 13 || slot.slot === 14;
      const style = `left:${slot.x/8}%;top:${slot.y/8}%;width:${slot.width/8}%;height:${slot.height/8}%;--tile-bg:${colors.background};--tile-fg:${colors.foreground};border-radius:${shape/8}cqw;`;
      return `<div class="preview-card ${card ? "" : "empty-card"} ${card && !card.visible ? "hidden-card" : ""} ${(selecting ? this._selectedCardIds.has(card?.id) : this._selectedSlot === slot.slot) ? "selected" : ""} ${compact ? "compact" : ""} ${strip ? "strip" : ""} ${sensor ? "data-card" : ""}" style="${style}" data-slot="${slot.slot}" data-action="slot" role="button" tabindex="${selecting && !card ? -1 : 0}" ${selecting && !card ? 'aria-disabled="true"' : ""} aria-label="${AEH_ESCAPE(card?.title || this.t("emptySlot"))}, ${this.t("slot")} ${slot.slot+1}" aria-pressed="${selecting ? this._selectedCardIds.has(card?.id) : this._selectedSlot === slot.slot}">
        ${card ? `<div class="tile-content">${sensor ? "" : this.icon(card.icon,'class="tile-icon"')}<span class="tile-title">${AEH_ESCAPE(card.title)}</span><span class="tile-state" data-live-slot="${slot.slot}">${AEH_ESCAPE(this.stateText(card))}</span></div>${selecting ? "" : `<button class="tile-drag" data-drag-kind="card" data-from="${slot.slot}" title="${this.t("drag")}" aria-label="${this.t("drag")} ${AEH_ESCAPE(card.title)}">${this.icon("mdi:drag")}</button>`}${!card.visible ? `<span class="hidden-badge">${this.t("hidden")}</span>` : ""}` : `<span class="empty-plus">+</span><span class="empty-label">${this.t("empty")}</span>`}
      </div>`;
    }).join("");
    return `<div class="screen" role="group" aria-label="${AEH_ESCAPE(page ? this.pageTitle(page) : this.t("preview"))}"><div class="screen-chrome">${this.icon("mdi:volume-high")}${this.icon("mdi:wifi")}</div><div class="screen-title">${AEH_ESCAPE(page ? this.pageTitle(page) : "")}</div>${cards}<div class="screen-dots"><i></i><i class="${this._pageId === "home-2" ? "current" : ""}"></i><i></i><i class="${this._pageId === "home-4" ? "current" : ""}"></i></div></div>`;
  }
  catalogueAreas(items) {
    const areas = new Map();
    for (const item of items.slice(0,500)) {
      if (typeof item?.area_id !== "string" || !item.area_id || item.area_id.length > 256) continue;
      if (!areas.has(item.area_id)) areas.set(item.area_id,{area_id:item.area_id,area_name:typeof item.area_name === "string" && item.area_name ? item.area_name.slice(0,80) : item.area_id});
    }
    return [...areas.values()].sort((a,b) => a.area_name.localeCompare(b.area_name) || a.area_id.localeCompare(b.area_id));
  }
  domainOptionsMarkup() {
    const domains = [...new Set([...this._entityIndex.values()].map(entity => entity.domain))].sort();
    return `<option value="">${this.t("all")}</option>`+domains.map(domain => `<option value="${AEH_ESCAPE(domain)}" ${domain === this._domain ? "selected" : ""}>${AEH_ESCAPE(domain.replaceAll("_"," "))}</option>`).join("");
  }
  areaOptionsMarkup() {
    return `<option value="">${this.t("allAreas")}</option><option value="none" ${this._area === "none" ? "selected" : ""}>${this.t("noArea")}</option>`+this._areas.map(area => `<option value="area:${AEH_ESCAPE(area.area_id)}" ${this._area === `area:${area.area_id}` ? "selected" : ""}>${AEH_ESCAPE(area.area_name)}</option>`).join("");
  }
  libraryMarkup() {
    if (this._catalogueError) return `<p class="inline-error">${AEH_ESCAPE(this._catalogueError)}</p><button data-action="retry">${this.t("retry")}</button>`;
    return `<p class="library-count">${this._catalogueTotal ?? this._catalogue.length} ${this.t("matches")}${this._truncated ? ` · ${this.t("more")}` : ""}</p>${this._areasTruncated ? `<p class="hint">${this.t("areaLimit")}</p>` : ""}<div class="entity-list">${this._catalogue.map(entity => `<div class="entity-row"><button class="entity-main" data-action="entity" data-entity="${AEH_ESCAPE(entity.entity_id)}" title="${this.t("add")}"><span class="entity-icon">${this.icon(({sun:"clock",light:"light",climate:"climate",cover:"cover",lock:"lock",alarm_control_panel:"alarm",fan:"fan",scene:"scene",switch:"switch"})[entity.domain] || "action")}</span><span class="entity-copy"><strong>${AEH_ESCAPE(entity.name)}</strong><small>${AEH_ESCAPE(entity.entity_id)}</small></span><span class="entity-state ${entity.available === false ? "unavailable" : ""}">${AEH_ESCAPE(entity.state)}</span></button><button class="entity-drag" data-drag-kind="entity" data-entity="${AEH_ESCAPE(entity.entity_id)}" title="${this.t("drag")}" aria-label="${this.t("drag")} ${AEH_ESCAPE(entity.name)}">${this.icon("mdi:drag")}</button></div>`).join("") || `<p class="empty-library">${this.t("noEntities")}</p>`}</div>`;
  }
  fieldMarkup(key,descriptor,value) {
    const attributes = `data-field="data:${AEH_ESCAPE(key)}" ${descriptor.required ? "required" : ""}`;
    let control;
    if (descriptor.type === "select" || descriptor.type === "boolean") {
      const values = descriptor.type === "boolean" ? [{value:"true",label:this.t("true")},{value:"false",label:this.t("false")}] : descriptor.options.map(option => ({value:option,label:option}));
      control = `<select ${attributes}><option value="">${this.t(descriptor.required ? "required" : "optional")}</option>${values.map(option => `<option value="${AEH_ESCAPE(option.value)}" ${String(value) === String(option.value) ? "selected" : ""}>${AEH_ESCAPE(option.label)}</option>`).join("")}</select>`;
    } else if (descriptor.type === "number") control = `<input type="number" ${attributes} ${descriptor.min === undefined ? "" : `min="${descriptor.min}"`} ${descriptor.max === undefined ? "" : `max="${descriptor.max}"`} step="${descriptor.step ?? "any"}" value="${AEH_ESCAPE(value ?? "")}" placeholder="${this.t(descriptor.required ? "required" : "optional")}">`;
    else control = `<input type="text" ${attributes} value="${AEH_ESCAPE(Array.isArray(value) ? value.join(", ") : value ?? "")}" placeholder="${this.t("rgb")}">`;
    return `<label>${AEH_ESCAPE(key.replaceAll("_"," "))}${control}</label>`;
  }
  inspectorMarkup() {
    if (this._selectingCards) return `<div class="empty-inspector"><h2>${this.t("multiActive")}</h2><p>${this.t("multiHint")}</p><p>${this.t("multiKeyboard")}</p></div>`;
    const slot = this.slotAt(this._selectedSlot), card = this.cardAt(this._selectedSlot);
    if (!slot) return `<div class="inspector-placeholder">${this.icon("mdi:cursor-default-click-outline")}<h2>${this.t("inspector")}</h2><p>${this.t("selectCard")}</p></div>`;
    const header = `<div class="inspector-heading"><span class="eyebrow">${this.t("slot")} ${slot.slot+1}</span><button class="icon-button" data-action="close-inspector" aria-label="${this.t("close")}">${this.icon("mdi:close")}</button></div>`;
    if (!card) return `${header}<h2>${this.t("empty")}</h2><p>${this.t("changeEntity")}</p>${this.pasteMarkup(slot.slot)}<button class="text-button" data-action="focus-library">${this.icon("mdi:magnify")}${this.t("search")}</button>`;
    const options = (values,selected) => values.map(value => `<option value="${AEH_ESCAPE(value)}" ${value === selected ? "selected" : ""}>${AEH_ESCAPE(value.replaceAll("_"," "))}</option>`).join("");
    const entity = this.entityFor(card.entity_id), actions = entity?.actions || [], action = actions.find(item => item.service === card.action.service);
    const controlKind = card.entity_id.startsWith("input_number.") ? "number" : "light";
    const lightControl = this.controlAvailability(card,controlKind), savedControl = card.action.kind === "control" && card.action.control === controlKind;
    const controlOption = lightControl.ready || savedControl ? `<option value="${controlKind === "number" ? "control-number" : "control"}" ${savedControl ? "selected" : ""} ${lightControl.ready ? "" : "disabled"}>${this.controlText("control",controlKind)}</option>` : "";
    const controlHint = savedControl || card.entity_id.startsWith("light.") || controlKind === "number" ? `<p class="hint" data-light-control-hint>${this.t(lightControl.reason)}</p>` : "";
    const sunHint = this.isSunCard(card) ? `<p class="hint" data-sun-placement>${this.t("sunPlacement")}</p>` : "";
    const actionNote = savedControl && controlKind === "number" ? "" : `<p class="hint">${this.t(savedControl ? "controlHint" : "actionsNote")}</p>`;
    const serviceMarkup = card.action.kind === "service" ? `<label>${this.t("service")}<select data-field="service" required><option value="">${this.t("chooseService")}</option>${actions.map(item => `<option value="${AEH_ESCAPE(item.service)}" ${card.action.service === item.service ? "selected" : ""}>${AEH_ESCAPE(item.service)}</option>`).join("")}${card.action.service && !action ? `<option selected value="${AEH_ESCAPE(card.action.service)}">${AEH_ESCAPE(card.action.service)}</option>` : ""}</select></label>${!actions.length ? `<p class="hint">${this.t("noActions")}</p>` : ""}${card.action.service && !action ? `<p class="inline-error">${this.t("actionUnavailable")}</p>` : ""}${action ? Object.entries(action.fields || {}).map(([key,descriptor]) => this.fieldMarkup(key,descriptor,card.action.data?.[key])).join("") : ""}` : "";
    return `${header}<h2>${AEH_ESCAPE(card.title || this.t("inspector"))}</h2><form id="properties" autocomplete="off">
      <section class="property-group"><label>${this.t("entity")}<span class="entity-reference">${AEH_ESCAPE(card.entity_id || this.t("noEntity"))}</span></label><button type="button" class="text-button" data-action="focus-library">${this.t("changeEntity")}</button>
      <label>${this.t("title")}<input data-field="title" value="${AEH_ESCAPE(card.title)}" maxlength="40"></label>
      <label>${this.t("type")}<select data-field="type">${["entity","sensor","action"].filter(type => slot.types.includes(type) && (!this.isSunCard(card) || type === "sensor")).map(type => `<option value="${type}" ${card.type === type ? "selected" : ""}>${this.t(type+"Type")}</option>`).join("")}</select></label></section>
      <section class="property-group"><label>${this.t("icon")}<select data-field="icon">${options(this._data.icons,card.icon)}</select></label><label>${this.t("palette")}<select data-field="palette">${options(this._data.palettes,card.palette)}</select></label><div class="palette-swatches">${this._data.palettes.map(palette => `<span data-palette="${AEH_ESCAPE(palette)}" style="background:${this.paletteColors(palette).background}" title="${AEH_ESCAPE(palette)}"></span>`).join("")}</div><label class="switch-row"><span>${this.t("visible")}</span><input data-field="visible" type="checkbox" ${card.visible ? "checked" : ""}></label></section>
      <section class="property-group"><label>${this.t("tap")}<select data-field="action-kind" ${card.type === "sensor" ? "disabled" : ""}>${["default","none","service"].map(kind => `<option value="${kind}" ${card.action.kind === kind ? "selected" : ""}>${this.t(kind)}</option>`).join("")}${controlOption}</select></label>${serviceMarkup}${controlHint}${actionNote}${sunHint}<p class="inline-error" data-field-error>${AEH_ESCAPE(Object.values(this._fieldErrors).join(" "))}</p></section>
      <section class="property-group"><label>${this.t("move")}<select id="move-target"><option value="">${this.t("choosePlace")}</option>${this.pages.map(page => `<optgroup label="${AEH_ESCAPE(this.pageTitle(page))}">${this.slots.filter(item => item.page_id === page.id && item.slot !== slot.slot && (!this.isSunCard(card) || this.acceptsCard(item,card)) && (!this.isSunCard(this.cardAt(item.slot)) || this.acceptsCard(slot,this.cardAt(item.slot)))).map(item => `<option value="${item.slot}">${this.t("slot")} ${item.slot+1} · ${AEH_ESCAPE(this.cardAt(item.slot)?.title || this.t("emptySlot"))}</option>`).join("")}</optgroup>`).join("")}</select></label><button class="text-button" type="button" data-action="copy-card" title="${this.t("copy")} (Ctrl/Cmd+C)">${this.icon("mdi:content-copy")}${this.t("copy")}</button><button class="text-button" type="button" data-action="cut-card" title="${this.t("cut")} (Ctrl/Cmd+X)">${this.icon("mdi:content-cut")}${this.t("cut")}</button><button class="danger text-button" type="button" data-action="remove">${this.icon("mdi:delete-outline")}${this.t("remove")}</button></section>
    </form>`;
  }
  statusMarkup() {
    const status = this._status, revision = status.saved_revision ?? this._saved?.revision;
    const validRevision = value => Number.isSafeInteger(value) && value >= 0;
    const sent = validRevision(status.sent_revision) ? `v${status.sent_revision}` : this.t("waiting");
    const applied = this.profile?.features?.applied_ack === true && validRevision(status.applied_revision) ? `v${status.applied_revision}` : this.t("unconfirmed");
    const connection = status.device_available === true ? "online" : status.device_available === false ? "offline" : "unknown";
    const accepted = status.context_press_version === 1 && validRevision(status.accepted_revision) ? status.accepted_revision : null;
    const stale = accepted !== null && accepted !== revision;
    const staleText = accepted < revision ? this.t("olderLayout") : this.t("differentLayout");
    const historical = connection !== "online" || this._statusError;
    const received = accepted === null ? this.t("unknown") : `v${accepted}${stale ? ` · ${staleText}` : ""}${historical ? ` · ${this.t("lastKnown")}` : ""}`;
    const mask = status.pending_slots, validMask = Number.isInteger(mask) && mask >= 0 && mask <= 0xFFFFFFFF;
    let snapshot = this.t("unconfirmed"), snapshotState = connection === "offline" ? "offline" : "unknown";
    if (!historical && accepted !== null) {
      if (stale) { snapshot = `${this.t("waiting")} · ${staleText}`; snapshotState = "stale"; }
      else if (status.snapshot_ready === true && (mask === null || mask === undefined || (validMask && mask === 0))) { snapshot = this.t("ready"); snapshotState = "ready"; }
      else if (status.snapshot_ready === false && (mask === null || mask === undefined || validMask)) {
        let count = 0, bits = validMask ? mask >>> 0 : 0;
        while (bits) { bits = (bits & (bits-1)) >>> 0; count++; }
        snapshot = count ? this.t("pendingPlaces").replace("{count}",count) : this.t("waiting"); snapshotState = "pending";
      }
    }
    return `<span class="connection ${connection}"><i></i>${this.t(connection)}</span><span>${this.t("saved")} <b>${validRevision(revision) ? `v${revision}` : "—"}</b></span><span>${this.t("sent")} <b>${sent}</b></span><span data-status="received">${this.t("received")} <b>${received}</b></span><span data-status="snapshot" data-snapshot-state="${snapshotState}">${this.t("snapshot")} <b>${snapshot}</b></span><span>${this.t("applied")} <b>${applied}</b></span>${this._statusError ? `<span class="status-warning">${this.t("refreshFailed")}</span>` : ""}<span class="status-note">${this.t("statusHint")}</span>`;
  }
  deviceIdentityMarkup() {
    const raw = this.entry?.device_identity;
    const identity = raw?.source === "home_assistant_device_registry" && raw.registry_entry_present === true ? raw : null;
    const value = key => typeof identity?.[key] === "string" && identity[key].trim() ? [...identity[key]].slice(0,80).join("") : this.t("unknown");
    const facts = [["deviceName","name"],["manufacturer","manufacturer"],["deviceModel","model"],["softwareVersion","software_version"]];
    const offline = !this.isConnected || this._statusError || this._status.device_available !== true;
    return `<p class="hint"><strong>${this.t("identityTitle")}</strong><br>${this.t("identityStored")}${!identity ? ` ${this.t("identityMissing")}` : offline ? ` ${this.t("identityOffline")}` : ""}</p><dl class="capabilities-grid">${facts.map(([label,key]) => `<div><dt>${this.t(label)}</dt><dd>${AEH_ESCAPE(value(key))}</dd></div>`).join("")}</dl>`;
  }
  capabilitiesMarkup() {
    const profile = this.profile || {}, slots = Array.isArray(profile.slots) ? profile.slots : null, pages = Array.isArray(profile.pages) ? profile.pages : null;
    const knownNumber = value => Number.isInteger(value) && value >= 0 ? value : this.t("unknown");
    const editable = slots?.filter(slot => slot.editable === true && slot.hidden !== true);
    const reserved = slots?.filter(slot => slot.editable === false || slot.hidden === true);
    const editablePages = pages && slots ? pages.filter(page => editable.some(slot => slot.page_id === page.id)).length : null;
    const resolution = Number.isInteger(profile.width) && profile.width > 0 && Number.isInteger(profile.height) && profile.height > 0 ? `${profile.width} × ${profile.height}` : this.t("unknown");
    const facts = [["profile",typeof profile.id === "string" && profile.id ? profile.id : this.t("unknown")],["resolution",resolution],
      ["places",`${knownNumber(profile.max_cards)} · ${editable ? editable.length : this.t("unknown")} ${this.t("editable")} · ${reserved ? reserved.length : this.t("unknown")} ${this.t("reservedPlaces")}`],
      ["pages",pages && editablePages !== null ? `${pages.length} · ${editablePages} ${this.t("editable")} · ${pages.length-editablePages} ${this.t("builtInPages")}` : this.t("unknown")]];
    const flags = [["move","featureMove"],["resize","featureResize"],["custom_pages","featurePages"],["native_controls","featureControls"],["applied_ack","featureApplied"]];
    return `<div id="device-identity">${this.deviceIdentityMarkup()}</div><p class="hint">${this.t("profileHint")}</p>${Array.isArray(profile.sun_text_slots) ? `<p class="hint" data-sun-capability>${this.t("sunPlacement")}</p>` : ""}<dl class="capabilities-grid">${facts.map(([key,value]) => `<div><dt>${this.t(key)}</dt><dd>${AEH_ESCAPE(value)}</dd></div>`).join("")}${flags.map(([key,label]) => `<div><dt>${this.t(label)}</dt><dd>${this.t(profile.features?.[key] === true ? "supported" : profile.features?.[key] === false ? "notSupported" : "unknown")}</dd></div>`).join("")}</dl>`;
  }
  feedbackMarkup() {
    const conflict = this._restoreConflict ? this.dt("conflict").replace("{base}",this._draftBaseRevision).replace("{current}",this._saved.revision) : this.t("conflict");
    return `${this._conflict ? `<div class="conflict" role="alert">${this.icon("mdi:source-branch")}<span>${AEH_ESCAPE(conflict)}</span><button data-action="${this._restoreConflict ? "review-draft" : "reload"}">${this._restoreConflict ? this.dt("review") : this.t("reload")}</button></div>` : ""}${this._error ? `<p class="feedback error" role="alert">${AEH_ESCAPE(this._error)}</p>` : ""}${this._notice ? `<p class="feedback" role="status">${AEH_ESCAPE(this._notice)}${this._recovery ? ` <button class="text-button" data-action="restore">${this.t("restore")}</button>` : ""}</p>` : ""}${this._storageError ? `<p class="feedback">${this.dt("unavailable")}</p>` : ""}`;
  }
  modalMarkup() {
    if (!this._pending) return "";
    if (this._pending.kind === "group-paste") {
      const pending = this._pending, current = this.groupPasteCurrent(), moving = pending.clipboard.mode === "group-cut";
      const rows = pending.cards.map((card,index) => {
        const page = this.pages.find(page => page.id === this.slotAt(card.slot)?.page_id);
        return `<label>${AEH_ESCAPE(card.title)}<span class="hint">${page ? AEH_ESCAPE(this.pageTitle(page))+" · " : ""}${this.t("slot")} ${card.slot+1}</span><select data-group-target="${index}" aria-label="${AEH_ESCAPE(this.t("groupTarget").replace("{title}",card.title))}" ${!current ? "disabled" : ""}>${this.groupTargetOptions(card,index)}</select></label>`;
      }).join("");
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><h2 id="modal-title">${this.t(moving ? "groupMoveTitle" : "groupTitle").replace("{count}",pending.cards.length)}</h2><p>${this.t(moving ? "groupCutHint" : "groupHint")}</p><div class="group-mapping">${rows}</div>${!current ? `<p class="inline-error">${this.t(moving && !this.groupCutSourceSlots() ? "groupCutChanged" : "groupChanged")}</p>` : ""}${this._error ? `<p class="inline-error" role="alert">${AEH_ESCAPE(this._error)}</p>` : ""}<div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="primary" data-action="modal-paste-group" ${!this.groupPasteReady() ? "disabled" : ""}>${this.t(moving ? "groupMove" : "groupPaste")}</button></div></section></div>`;
    }
    if (this._pending.kind === "bulk-style") {
      const pending = this._pending, current = this.selectedStyleCurrent();
      if (this._pending !== pending) return "";
      const options = pending.palettes.map(palette => `<option value="${AEH_ESCAPE(palette)}" ${palette === pending.palette ? "selected" : ""}>${this.t(AEH_PALETTE_LABELS[palette])}</option>`).join("");
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><h2 id="modal-title">${this.t("styleTitle").replace("{count}",pending.cards.length)}</h2><p>${this.t("styleHint")}</p><ul class="selection-review">${pending.cards.map(card => `<li>${AEH_ESCAPE(card.title)} · ${AEH_ESCAPE(this.pageTitle(this.profile.pages.find(page => page.id === this.slotAt(card.slot)?.page_id) || {}))} · ${this.t("slot")} ${card.slot+1}</li>`).join("")}</ul><div class="group-mapping"><label>${this.t("palette")}<select data-selected-style aria-label="${this.t("palette")}" ${!current || this._busy ? "disabled" : ""}><option value="" ${pending.palette === null ? "selected" : ""}>${this.t("styleUnchanged")}</option>${options}</select></label></div>${!current ? `<p class="inline-error">${this.t("styleChanged")}</p>` : ""}${this._error ? `<p class="inline-error" role="alert">${AEH_ESCAPE(this._error)}</p>` : ""}<div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="primary" data-action="modal-style-selected" ${!this.selectedStyleReady() ? "disabled" : ""}>${this.t("styleApply")}</button></div></section></div>`;
    }
    if (this._pending.kind === "bulk-delete") {
      const pending = this._pending, cards = pending.cards, current = this.selectedDeleteCurrent();
      if (this._pending !== pending) return "";
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><h2 id="modal-title">${this.t("multiDeleteTitle").replace("{count}",cards.length)}</h2><p>${this.t("multiDeleteHint")}</p><ul class="selection-review">${cards.map(card => `<li>${AEH_ESCAPE(card.title)} · ${this.t("slot")} ${card.slot+1}</li>`).join("")}</ul>${!current ? `<p class="inline-error">${this.t("multiChanged")}</p>` : ""}<div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="danger" data-action="modal-batch-delete" ${!current || this._busy ? "disabled" : ""}>${this.t("multiDeleteConfirm").replace("{count}",cards.length)}</button></div></section></div>`;
    }
    if (this._pending.kind === "light-control") {
      const card = this.cardAt(this._pending.slot);
      const controlKind = this._pending.controlKind || "light";
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><span class="modal-symbol">${this.icon(controlKind === "number" ? "mdi:numeric" : "light")}</span><h2 id="modal-title">${this.controlText("controlReviewTitle",controlKind)}</h2><p>${this.controlText(this._draft.version === 2 ? "controlReviewV2" : "controlReviewV3",controlKind)}</p><div class="import-summary">${AEH_ESCAPE(card?.title)}<br>${AEH_ESCAPE(card?.entity_id)}</div><p class="hint">${this.t(this.controlAvailability(card,controlKind).reason)}</p><div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="primary" data-action="modal-light-control" ${this._busy || !this.lightControlReviewCurrent() ? "disabled" : ""}>${this.controlText("controlConfirm",controlKind)}</button></div></section></div>`;
    }
    const imported = this._pending.kind === "import", restoring = this._pending.kind === "restore";
    const heading = restoring ? this.dt("title") : this.t(imported ? "importTitle" : "switchTitle");
    const hint = restoring ? this.dt("hint") : this.t(imported ? "importHint" : "switchHint");
    const restoreConflict = restoring && this._pending.record.base_revision !== this._saved.revision;
    const details = restoring ? `<div class="import-summary">v${this._pending.record.base_revision} → v${this._saved.revision}</div>${restoreConflict ? `<p class="hint">${AEH_ESCAPE(this.dt("conflict").replace("{base}",this._pending.record.base_revision).replace("{current}",this._saved.revision))}</p>` : ""}` : imported ? `<div class="import-summary">${this.t("importCount")} <strong>${this._pending.layout.cards.filter(card => card.slot > 1).length}</strong> ${this.t("cards")}.</div>${this._pending.warnings.map(warning => `<p class="hint">${AEH_ESCAPE(typeof warning === "string" ? warning : warning.message || JSON.stringify(warning))}</p>`).join("")}` : "";
    const controls = restoring ? `<button data-action="modal-discard-draft">${this.dt("discard")}</button><button class="primary" data-action="modal-restore">${this.dt("restore")}</button>` : `<button data-action="modal-cancel">${this.t(imported ? "cancel" : "stay")}</button>${imported ? `<button class="primary" data-action="modal-import">${this.t("useImport")}</button>` : `<button data-action="modal-discard">${this.t("discardSwitch")}</button><button class="primary" data-action="modal-save" ${this._conflict || this._busy ? "disabled" : ""}>${this.t("saveSwitch")}</button>`}`;
    return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><span class="modal-symbol">${this.icon(imported || restoring ? "mdi:file-import-outline" : "mdi:content-save-outline")}</span><h2 id="modal-title">${heading}</h2><p>${hint}</p>${details}${this._error ? `<p class="inline-error" role="alert">${AEH_ESCAPE(this._error)}</p>` : ""}${!restoring && this._conflict ? `<p class="inline-error">${this.t("conflict")}</p>` : ""}<div class="modal-actions">${controls}</div></section></div>`;
  }

  render() {
    this.syncCardSelection();
    if (!this._data || !this.entry) {
      this.shadowRoot.innerHTML = `<style>${this.styles()}</style><main class="loading"><div class="brand-mark"><i></i><i></i><i></i><i></i></div><h1>Atmosfera</h1><p>${AEH_ESCAPE(this._error || (this._data ? this.t("noDevices") : this.t("loading")))}</p>${this._error ? `<button data-action="retry">${this.t("retry")}</button>` : ""}</main>`; return;
    }
    this.shadowRoot.innerHTML = `<style>${this.styles()}</style><main>
      <header class="app-header"><div class="brand"><div class="brand-mark" aria-hidden="true"><i></i><i></i><i></i><i></i></div><div><span class="eyebrow">Atmosfera</span><h1>${this.t("heading")}</h1><p>${this.t("intro")}</p></div></div><div class="header-actions"><label class="device-picker">${this.t("display")}<select id="device">${this._data.entries.map(entry => `<option value="${AEH_ESCAPE(entry.entry_id)}" ${entry.entry_id === this._entryId ? "selected" : ""}>${AEH_ESCAPE(entry.title)}</option>`).join("")}</select></label><button class="primary save-button" data-action="save">${this.icon("mdi:content-save-outline")}<span data-save-label>${this.t("save")}</span></button></div></header>
      <div class="status-row" id="delivery-status">${this.statusMarkup()}</div>
      <details class="device-capabilities" id="device-capabilities"><summary>${this.t("capabilities")}</summary><div id="device-capabilities-body">${this.capabilitiesMarkup()}</div></details>
      <div id="feedback">${this.feedbackMarkup()}</div>
      <div class="editor-shell"><aside class="library"><div class="section-heading"><span class="section-symbol">${this.icon("mdi:home-variant-outline")}</span><h2>${this.t("library")}</h2></div><label class="search-box">${this.icon("mdi:magnify")}<input id="search" type="search" maxlength="128" value="${AEH_ESCAPE(this._query)}" placeholder="${this.t("search")}" aria-label="${this.t("search")}"></label><label class="domain-filter"><select id="domain" aria-label="${this.t("all")}">${this.domainOptionsMarkup()}</select></label><label class="domain-filter"><select id="area" aria-label="${this.t("area")}">${this.areaOptionsMarkup()}</select></label><div id="library-results">${this.libraryMarkup()}</div></aside>
      <section class="workspace"><div class="workspace-tools"><div><span class="eyebrow">${this.t("preview")}</span><h2>${this.t("fixed")}</h2></div><div class="history-actions"><button class="icon-button" data-action="undo" aria-label="${this.t("undo")}" title="${this.t("undo")} (Ctrl+Z)">${this.icon("mdi:undo")}</button><button class="icon-button" data-action="redo" aria-label="${this.t("redo")}" title="${this.t("redo")} (Ctrl+Shift+Z)">${this.icon("mdi:redo")}</button></div></div><div id="card-selection">${this.cardSelectionMarkup()}</div><div id="card-clipboard">${this.clipboardMarkup()}</div><nav class="page-tabs" id="page-tabs" role="tablist">${this.pageMarkup()}</nav><div class="device-stage" id="device-preview">${this.previewMarkup()}</div><p class="preview-caption">${this.t("previewHint")}</p><p class="keyboard-hint">${this.icon("mdi:cursor-move")}${this.t("keyboard")}</p><div class="workspace-bottom"><span class="dirty-indicator" id="dirty-state"></span><div><button class="text-button" data-action="import">${this.icon("mdi:file-import-outline")}${this.t("import")}</button><button class="text-button" data-action="export" title="${this.t("exportHint")}">${this.icon("mdi:download")}${this.t("export")}</button></div></div><input id="import-file" type="file" accept=".json,application/json" hidden></section>
      <aside class="inspector" id="inspector">${this.inspectorMarkup()}</aside></div>
      <div class="sr-only" id="announcement" aria-live="polite" aria-atomic="true"></div><div id="modal-host">${this.modalMarkup()}</div>
    </main>`;
    // Seed original source strings: HTML serialization can normalize escaped
    // text, so comparing only innerHTML would still replace unchanged controls.
    for (const [selector,markup] of [["#card-selection",this.cardSelectionMarkup()],["#delivery-status",this.statusMarkup()],["#card-clipboard",this.clipboardMarkup()],["#feedback",this.feedbackMarkup()],["#modal-host",this.modalMarkup()],["#library-results",this.libraryMarkup()],["#domain",this.domainOptionsMarkup()],["#area",this.areaOptionsMarkup()],["#inspector",this.inspectorMarkup()]]) {
      const target = this.shadowRoot.querySelector(selector); if (target) this._paintedMarkup.set(target,markup);
    }
    this.paintToolbar();
  }
  paintLibrary() {
    this.paintMarkup("#library-results",this.libraryMarkup());
    this.paintMarkup("#domain",this.domainOptionsMarkup());
    this.paintMarkup("#area",this.areaOptionsMarkup());
    for (const [selector,value] of [["#domain",this._domain],["#area",this._area]]) {
      const picker = this.shadowRoot.querySelector(selector); if (picker && picker.value !== value) picker.value = value;
    }
  }
  paintInspector() { this.paintMarkup("#inspector",this.inspectorMarkup()); }
  paintClipboard() { this.paintMarkup("#card-clipboard",this.clipboardMarkup()); }
  paintPages() { const target = this.shadowRoot.querySelector("#page-tabs"); if (target) target.innerHTML = this.pageMarkup(); }
  paintPreview() { const target = this.shadowRoot.querySelector("#device-preview"); if (target) target.innerHTML = this.previewMarkup(); }
  paintMarkup(selector,markup) {
    const target = this.shadowRoot.querySelector(selector);
    if (!target || this._paintedMarkup.get(target) === markup) return false;
    if (target.innerHTML === markup) { this._paintedMarkup.set(target,markup); return false; }
    const focused = this.shadowRoot.activeElement;
    const action = focused?.tagName === "BUTTON" && target.contains(focused) ? focused.dataset.action : null;
    target.innerHTML = markup; this._paintedMarkup.set(target,markup);
    if (action) [...target.querySelectorAll("button[data-action]")].find(button => button.dataset.action === action)?.focus();
    return true;
  }
  paintStatus() { this.paintMarkup("#delivery-status",this.statusMarkup()); this.paintMarkup("#device-identity",this.deviceIdentityMarkup()); }
  paintFeedback() { this.paintMarkup("#feedback",this.feedbackMarkup()); if (this._pending) this.renderModal(); }
  paintModalFocus() { (this._pending?.kind === "bulk-style" ? this.shadowRoot.querySelector(".modal select:not([disabled])") || this.shadowRoot.querySelector(".modal button") : this._pending?.kind === "group-paste" ? this.shadowRoot.querySelector(".modal select") || this.shadowRoot.querySelector(".modal button") : this.shadowRoot.querySelector(".modal button"))?.focus(); }
  renderModal() {
    const changed = this.paintMarkup("#modal-host",this.modalMarkup());
    if (changed && this._pending && !this.shadowRoot.querySelector("#modal-host").contains(this.shadowRoot.activeElement)) this.paintModalFocus();
  }
  paintValues() {
    if (this.syncCardSelection()) { this.paintPreview(); this.paintInspector(); this.renderModal(); this.paintToolbar(); }
    const previous = this._cardClipboard; this.clipboardCard();
    if (previous && !this._cardClipboard) {
      this.paintClipboard(); this.renderModal();
      if (!this.shadowRoot.querySelector("#inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
      this.paintToolbar();
    }
    this.shadowRoot.querySelectorAll("[data-live-slot]").forEach(label => {
      const value = this.stateText(this.cardAt(label.dataset.liveSlot)); if (label.textContent !== value) label.textContent = value;
    });
  }
  paintToolbar() {
    this.paintCardSelection();
    this.shadowRoot.querySelectorAll(".modal button").forEach(button => { button.disabled = this._busy || (button.dataset.action === "modal-save" && this._conflict) || (button.dataset.action === "modal-light-control" && !this.lightControlReviewCurrent()) || (button.dataset.action === "modal-batch-delete" && !this.selectedDeleteCurrent()) || (button.dataset.action === "modal-paste-group" && !this.groupPasteReady()) || (button.dataset.action === "modal-style-selected" && !this.selectedStyleReady()); });
    this.shadowRoot.querySelectorAll("[data-selected-style]").forEach(select => { const disabled = this._busy || !this.selectedStyleCurrent(); if (select.disabled !== disabled) select.disabled = disabled; });
    this.shadowRoot.querySelectorAll("#properties input,#properties select,#properties button,#device,[data-action=import],[data-action=export],[data-action=remove]").forEach(control => {
      control.disabled = this._busy || (this._selectingCards && control.dataset?.action === "import") || (control.dataset?.field === "action-kind" && this.cardAt(this._selectedSlot)?.type === "sensor");
    });
    this.shadowRoot.querySelectorAll('[data-action="save"]').forEach(button => {
      button.disabled = this._busy || !this.dirty || this._conflict || !!Object.keys(this._fieldErrors).length;
      const label = button.querySelector("[data-save-label]"), value = this.t(this._busy ? "saving" : "save"); if (label && label.textContent !== value) label.textContent = value;
    });
    this.shadowRoot.querySelectorAll('[data-action="paste-group"]').forEach(button => { button.disabled = !this.canReviewGroupPaste(); });
    this.shadowRoot.querySelectorAll('[data-action="paste-card"]').forEach(button => { button.disabled = !this.canPasteCard(); });
    this.shadowRoot.querySelectorAll('[data-action="copy-card"],[data-action="cut-card"]').forEach(button => { button.disabled = this.clipboardDisconnected() || this._busy || !!this._pending || !!this._drag || !!this._carry || !!Object.keys(this._fieldErrors).length || (button.dataset.action === "cut-card" && this._profileStale); });
    this.shadowRoot.querySelectorAll('[data-action="clear-copy"]').forEach(button => { button.disabled = this._busy; });
    for (const direction of ["undo","redo"]) {
      const button = this.shadowRoot.querySelector(`[data-action="${direction}"]`);
      if (button) button.disabled = this._busy || !this[`_${direction}`].length;
    }
    const dirty = this.shadowRoot.querySelector("#dirty-state");
    if (dirty) {
      const value = this.t(this.dirty ? "dirty" : "clean")+(this.dirty && this._draftStored ? ` · ${this.dt("local")}` : "");
      if (dirty.textContent !== value) dirty.textContent = value;
      dirty.classList.toggle("has-changes",this.dirty);
    }
  }
  styles() {
    return `
      .group-mapping{display:grid;gap:12px;max-height:min(52vh,480px);overflow:auto;margin:16px 0}.group-mapping label{display:grid;gap:6px;font-size:12px;overflow-wrap:anywhere}.group-mapping select{width:100%;min-height:44px;padding:8px;border:1px solid var(--a-border);border-radius:12px;color:inherit;background:var(--a-surface)}
      .selection-tools{display:flex;flex-direction:column;gap:10px;margin:12px 0;padding:14px;border-radius:18px;background:var(--a-tonal);font-size:12px}.selection-tools>div{display:flex;flex-wrap:wrap;gap:6px}.selection-tools p{font-size:11px;line-height:1.5;color:var(--a-muted)}.selection-tools button{font-size:11px;min-height:44px}.selection-review{max-height:240px;overflow:auto;padding-left:20px;overflow-wrap:anywhere;line-height:1.7}.preview-card[aria-disabled=true]{cursor:default}
      .status-note{flex-basis:100%;font-size:10px;line-height:1.5}.device-capabilities{margin:-8px 0 20px;border:1px solid var(--a-border);border-radius:18px;background:var(--a-surface);font-size:12px}.device-capabilities summary{padding:12px 16px;cursor:pointer;font-weight:550}.device-capabilities summary:focus-visible{outline:3px solid var(--a-primary);outline-offset:3px;border-radius:18px}.device-capabilities>div{padding:0 16px 14px}.capabilities-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px 20px;margin:0}.capabilities-grid div{min-width:0}.capabilities-grid dt{font-size:10px;color:var(--a-muted);margin-bottom:4px}.capabilities-grid dd{margin:0;overflow-wrap:anywhere;line-height:1.5}.clipboard-note{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px;margin-top:14px;border-radius:16px;background:var(--a-tonal);font-size:11px;line-height:1.5}.clipboard-note>div{flex:1;min-width:160px;overflow-wrap:anywhere}.clipboard-note p{color:var(--a-muted);font-size:10px;margin-top:4px}.clipboard-note .text-button{font-size:10px;min-height:40px}
      :host{display:block;color:var(--primary-text-color,#252331);font-family:var(--paper-font-body1_-_font-family,Roboto,system-ui,sans-serif);--a-primary:var(--primary-color,#7450c6);--a-on-primary:var(--text-primary-color,#fff);--a-bg:var(--primary-background-color,#f8f7fb);--a-surface:var(--card-background-color,#fff);--a-tonal:color-mix(in srgb,var(--a-primary) 10%,var(--a-surface));--a-border:color-mix(in srgb,var(--primary-text-color,#252331) 11%,transparent);--a-muted:var(--secondary-text-color,#6b6676);background:var(--a-bg);min-height:100vh}
      *{box-sizing:border-box}button,input,select{font:inherit}button{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:1px solid var(--a-border);border-radius:22px;min-height:44px;padding:9px 15px;color:inherit;background:var(--a-surface);cursor:pointer;transition:background .16s,box-shadow .16s,transform .16s}button:hover:not(:disabled){background:var(--a-tonal)}button:active:not(:disabled){transform:scale(.98)}button:disabled{opacity:.42;cursor:default}button:focus-visible,input:focus-visible,select:focus-visible,[role=button]:focus-visible{outline:3px solid var(--a-primary);outline-offset:4px}ha-icon{--mdc-icon-size:22px;display:inline-flex;width:var(--mdc-icon-size);height:var(--mdc-icon-size);flex:none}h1,h2,p{margin:0}h1{font-size:30px;line-height:1.15;font-weight:650;letter-spacing:-.8px}h2{font-size:18px;font-weight:600;letter-spacing:-.2px}main{max-width:1760px;margin:auto;padding:28px clamp(16px,2.2vw,40px) 36px}.app-header,.header-actions,.brand,.status-row,.section-heading,.workspace-tools,.workspace-bottom{display:flex;align-items:center}.app-header{justify-content:space-between;gap:24px;margin-bottom:20px}.brand{gap:16px}.brand-mark{width:54px;height:54px;display:grid;grid-template-columns:1fr 1fr;gap:4px;transform:rotate(-8deg);flex:none}.brand-mark i{background:var(--a-primary);border-radius:50% 50% 10px 50%}.brand-mark i:nth-child(2){opacity:.65;transform:rotate(80deg)}.brand-mark i:nth-child(3){opacity:.4;transform:rotate(185deg)}.brand-mark i:nth-child(4){opacity:.8;transform:rotate(265deg)}.eyebrow{display:block;font-size:11px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:var(--a-muted);margin-bottom:5px}.brand p{margin-top:7px;font-size:13px;color:var(--a-muted)}.header-actions{gap:12px}.device-picker{display:grid;gap:5px;font-size:11px;color:var(--a-muted);min-width:190px}.device-picker select{min-height:43px;border-radius:16px;background:var(--a-surface);padding:9px 14px}.primary{background:var(--a-primary);color:var(--a-on-primary);border-color:transparent}.primary:hover:not(:disabled){background:color-mix(in srgb,var(--a-primary) 90%,#000)}.save-button{min-height:50px;padding:12px 22px;border-radius:26px;align-self:end;font-weight:600}.status-row{gap:8px 20px;flex-wrap:wrap;font-size:11px;color:var(--a-muted);padding:12px 16px;border-radius:18px;background:var(--a-surface);margin-bottom:20px}.status-row b{font-weight:550;color:var(--primary-text-color)}.connection{display:flex;align-items:center;gap:6px}.connection i{width:7px;height:7px;border-radius:50%;background:#9c94a6}.connection.online i{background:#398064}.connection.offline i{background:#a8704b}.status-warning{color:var(--warning-color,#b26a00)}
      .editor-shell{display:grid;grid-template-columns:minmax(220px,285px) minmax(330px,1fr) minmax(245px,305px);gap:18px;align-items:start}.library,.workspace,.inspector{border:1px solid var(--a-border);border-radius:28px;background:var(--a-surface);min-width:0}.library{padding:21px 14px 16px;position:sticky;top:16px;max-height:calc(100vh - 32px);overflow:auto}.section-heading{gap:10px;padding:0 6px;margin-bottom:18px}.section-heading h2{font-size:16px}.section-symbol{display:grid;place-items:center;width:35px;height:35px;border-radius:14px;background:var(--a-tonal);color:var(--a-primary)}.search-box{display:flex;align-items:center;gap:8px;background:var(--a-bg);border:1px solid var(--a-border);border-radius:18px;padding:0 12px;min-height:46px}.search-box ha-icon{color:var(--a-muted);--mdc-icon-size:20px}.search-box input{width:100%;min-width:0;padding:12px 0;background:transparent;border:0;outline:0;color:inherit;font-size:13px}.search-box:focus-within{box-shadow:0 0 0 2px var(--a-primary)}.domain-filter{margin:10px 0 0}.domain-filter select{min-height:35px;font-size:12px;border:0;padding:6px 10px;background:transparent}.library-count{font-size:10px;color:var(--a-muted);margin:12px 7px}.entity-list{display:grid;gap:4px}.entity-row{display:flex;align-items:center;border-radius:17px;min-width:0}.entity-row:hover{background:var(--a-tonal)}.entity-main{border:0;background:none;padding:10px 3px 10px 7px;min-width:0;flex:1;justify-content:start;border-radius:17px;text-align:left;gap:9px}.entity-copy{display:flex;flex-direction:column;min-width:0;flex:1;gap:4px}.entity-copy strong{font-size:12px;font-weight:550;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity-copy small{font-size:9px;color:var(--a-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity-icon{display:grid;place-items:center;background:var(--a-bg);border-radius:12px;width:34px;height:34px;color:var(--a-primary);flex:none}.entity-icon ha-icon{--mdc-icon-size:19px}.entity-state{font-size:10px;color:var(--a-muted);max-width:50px;overflow:hidden;text-overflow:ellipsis}.entity-state.unavailable{opacity:.5}.entity-drag{width:32px;min-width:32px;min-height:44px;padding:5px;border:0;background:none;color:var(--a-muted);touch-action:none}.entity-drag ha-icon{--mdc-icon-size:18px}.empty-library{padding:20px 8px;color:var(--a-muted);font-size:13px}
      .workspace{padding:22px;overflow:hidden;background:color-mix(in srgb,var(--a-bg) 64%,var(--a-surface))}.workspace-tools{justify-content:space-between;gap:8px}.workspace-tools h2{font-size:18px}.history-actions{display:flex;gap:3px}.icon-button{width:40px;min-height:40px;padding:8px;border:0;background:transparent;border-radius:50%}.page-tabs{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px;margin:20px 0 18px}.page-tab{font-size:11px;min-height:36px;padding:7px 12px;border:0;gap:6px;background:transparent}.page-tab ha-icon{--mdc-icon-size:16px}.page-tab.active{background:var(--a-primary);color:var(--a-on-primary)}.reserved-page{display:flex;align-items:center;gap:5px;font-size:10px;color:var(--a-muted);padding:6px;opacity:.6}.reserved-page ha-icon{--mdc-icon-size:14px}.device-stage{max-width:560px;margin:auto;padding:9px;background:#202028;border-radius:50%;box-shadow:0 20px 42px #1510221f,0 2px 8px #15102220}.screen{width:100%;aspect-ratio:1;background:#000;border-radius:50%;position:relative;container-type:inline-size;overflow:hidden;color:#fff}.screen-chrome{position:absolute;top:1.375%;left:42.375%;width:13.75%;display:flex;gap:.5cqw;align-items:center;color:#fff}.screen-chrome ha-icon{--mdc-icon-size:5.5cqw}.screen-chrome ha-icon:last-child{--mdc-icon-size:7.25cqw;transform:translateY(-1.5cqw)}.screen-title{position:absolute;left:27.5%;top:9.5%;width:45%;text-align:center;font-size:3cqw;line-height:1.2;color:#f5eefb}.preview-card{position:absolute;background:var(--tile-bg);color:var(--tile-fg);border:0;cursor:pointer;transition:box-shadow .16s,opacity .16s;outline:0;display:flex;justify-content:center;align-items:center}.preview-card:hover{box-shadow:inset 0 0 0 1px #ffffff70}.preview-card.selected{box-shadow:0 0 0 3px #fff,0 0 0 6px var(--a-primary)}.preview-card:focus-visible{outline:3px solid #fff;outline-offset:5px}.preview-card.drop-target{outline:5px dashed #fff;outline-offset:5px;box-shadow:0 0 0 9px var(--a-primary)}.tile-content{position:absolute;inset:0;display:flex;align-items:center;flex-direction:column;pointer-events:none;overflow:hidden;border-radius:inherit}.tile-content ha-icon.tile-icon{--mdc-icon-size:8.5cqw;position:absolute;top:21%}.tile-title,.tile-state{display:block;position:absolute;width:84%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:center;line-height:1.2}.tile-title{font-size:3cqw;bottom:23.4%}.tile-state{font-size:2cqw;bottom:11.3%;opacity:.82}.compact .tile-content .tile-icon{--mdc-icon-size:4.5cqw;top:12%}.compact .tile-title{font-size:2.5cqw;bottom:29.3%;width:88%}.compact .tile-state{font-size:2cqw;bottom:10.3%}.preview-card[data-slot="5"] .tile-content .tile-icon,.preview-card[data-slot="11"] .tile-content .tile-icon{--mdc-icon-size:5.5cqw;left:9.5%;top:29.3%}.preview-card[data-slot="5"] .tile-title,.preview-card[data-slot="11"] .tile-title{left:29.1%;top:18.1%;bottom:auto;width:60.1%;text-align:left;font-size:3cqw}.preview-card[data-slot="5"] .tile-state,.preview-card[data-slot="11"] .tile-state{left:29.1%;top:52.6%;bottom:auto;width:60.1%;text-align:left}.strip .tile-content .tile-icon{--mdc-icon-size:4.5cqw;left:9.5%;top:26.3%}.strip .tile-title{left:21.8%;top:15.8%;bottom:auto;width:66%;text-align:left;font-size:3cqw}.strip .tile-state{left:21.8%;top:56.6%;bottom:auto;width:66%;text-align:left}.data-card .tile-title{top:16%;bottom:auto;font-size:2cqw}.data-card .tile-state{top:46%;bottom:auto;font-size:4.25cqw;opacity:1}.preview-card[data-slot="13"] .tile-title{top:auto;bottom:16.1%}.preview-card[data-slot="13"] .tile-state{top:16.1%;bottom:auto}.tile-drag{position:absolute;top:5px;right:6px;z-index:1;width:32px;min-height:32px;padding:5px;border:0;background:#0002;color:inherit;opacity:0;touch-action:none;border-radius:50%}.tile-drag ha-icon{--mdc-icon-size:17px}.preview-card:hover .tile-drag,.preview-card.selected .tile-drag,.preview-card:focus-within .tile-drag{opacity:1}.hidden-card .tile-content{opacity:.3}.hidden-card{background:color-mix(in srgb,var(--tile-bg) 35%,#000);border:1px dashed #b9b2c6}.hidden-badge{position:absolute;left:50%;top:45%;transform:translate(-50%,-50%);font-size:2cqw;background:#000b;color:#fff;padding:4px 8px;border-radius:12px;pointer-events:none}.empty-card{background:#17151c;color:#aaa0b7;border:1px dashed #71677f;flex-direction:column;gap:4px}.empty-plus{font-size:6cqw;font-weight:300;line-height:1}.empty-label{font-size:2.2cqw}.screen-dots{position:absolute;bottom:7.8%;left:42%;right:42%;display:flex;gap:10%;align-items:center;justify-content:center}.screen-dots i{display:block;width:8%;aspect-ratio:1;border-radius:50%;background:#55515e}.screen-dots i.current{width:18%;aspect-ratio:2;background:#fff;border-radius:9px}.preview-caption{text-align:center;max-width:480px;margin:17px auto 0;color:var(--a-muted);font-size:11px;line-height:1.6}.keyboard-hint{display:flex;align-items:center;justify-content:center;gap:5px;color:var(--a-muted);font-size:10px;margin:10px 0 0}.keyboard-hint ha-icon{--mdc-icon-size:15px}.workspace-bottom{justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:20px;padding-top:14px;border-top:1px solid var(--a-border)}.workspace-bottom>div{display:flex;gap:2px}.text-button{border:0;background:transparent;padding:7px 9px;font-size:11px;min-height:36px;color:var(--a-primary)}.text-button ha-icon{--mdc-icon-size:17px}.dirty-indicator{font-size:10px;color:var(--a-muted)}.dirty-indicator.has-changes{color:var(--a-primary);font-weight:600}.dirty-indicator.has-changes:before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:currentColor;margin-right:6px}
      .inspector{padding:20px;position:sticky;top:16px;max-height:calc(100vh - 32px);overflow:auto}.inspector-heading{display:flex;justify-content:space-between;align-items:center;margin:-5px -7px 10px 0}.inspector h2{overflow-wrap:anywhere;margin-bottom:18px;font-size:21px;line-height:1.2}.inspector label{display:grid;gap:7px;font-size:11px;color:var(--a-muted);margin-bottom:13px}.inspector input,.inspector select{width:100%;min-width:0;min-height:43px;border:1px solid var(--a-border);border-radius:13px;padding:10px;color:var(--primary-text-color);background:var(--a-bg);font-size:12px}.inspector input[aria-invalid=true]{border-color:var(--error-color,#b3261e)}.entity-reference{font-family:ui-monospace,monospace;font-size:11px;color:var(--primary-text-color);overflow-wrap:anywhere;line-height:1.5}.property-group{border-top:1px solid var(--a-border);padding-top:17px;margin-top:6px}.property-group:first-child{padding-top:0;border:0}.property-group .text-button{margin:-7px 0 10px;padding-left:0;text-align:left;justify-content:start}.inspector .switch-row{display:flex;align-items:center;justify-content:space-between;min-height:37px;gap:12px;color:var(--primary-text-color)}.switch-row input{appearance:none;width:42px;min-height:25px;height:25px;border-radius:18px;border:0;background:#a9a1b4;position:relative;cursor:pointer;flex:none;padding:3px}.switch-row input:before{content:"";position:absolute;left:3px;top:3px;width:19px;height:19px;border-radius:50%;background:white;transition:transform .16s}.switch-row input:checked{background:var(--a-primary)}.switch-row input:checked:before{transform:translateX(17px)}.palette-swatches{display:flex;gap:7px;margin:-3px 0 14px}.palette-swatches span{width:23px;height:23px;border-radius:50%;border:1px solid var(--a-border)}.hint{font-size:10px;color:var(--a-muted);line-height:1.6;margin-bottom:13px}.inline-error,.error{color:var(--error-color,#b3261e)}.inline-error{font-size:11px;line-height:1.6}.danger{color:inherit;border-color:var(--error-color,#b3261e)}.inspector-placeholder{text-align:center;color:var(--a-muted);padding:24px 5px}.inspector-placeholder>ha-icon{--mdc-icon-size:40px;color:var(--a-primary);margin:0 auto 18px}.inspector-placeholder h2{font-size:17px;color:var(--primary-text-color);margin-bottom:9px}.inspector-placeholder p,.inspector>p{font-size:12px;line-height:1.6;margin-bottom:15px}.tonal{background:var(--a-tonal);border:0;color:var(--a-primary);font-size:12px}.feedback{font-size:12px;line-height:1.6;margin:-5px 6px 15px}.conflict{display:flex;align-items:center;gap:12px;flex-wrap:wrap;border-radius:20px;padding:13px 17px;margin-bottom:16px;background:color-mix(in srgb,var(--warning-color,#e8aa33) 13%,var(--a-surface));font-size:12px}.conflict span{flex:1}.conflict button{font-size:11px;min-height:35px}.drag-ghost{position:fixed;pointer-events:none;z-index:9999;max-width:240px;padding:13px 20px;border-radius:18px;background:var(--a-primary);color:var(--a-on-primary);font-size:13px;box-shadow:0 10px 40px #0004}
      .modal-shade{position:fixed;inset:0;z-index:10000;background:#17101f80;display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px)}.modal{max-width:470px;width:100%;padding:30px;border-radius:32px;background:var(--a-surface);box-shadow:0 24px 80px #0004;max-height:90vh;overflow:auto}.modal-symbol{width:50px;height:50px;border-radius:18px;display:grid;place-items:center;background:var(--a-tonal);color:var(--a-primary);margin-bottom:20px}.modal-symbol ha-icon{--mdc-icon-size:27px}.modal h2{font-size:25px;line-height:1.15;margin-bottom:13px}.modal>p{font-size:13px;line-height:1.65;color:var(--a-muted)}.modal-actions{display:flex;justify-content:end;gap:8px;flex-wrap:wrap;margin-top:25px}.modal-actions button{font-size:12px}.import-summary{padding:16px;margin-top:18px;background:var(--a-tonal);border-radius:18px;font-size:13px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.loading{min-height:60vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px}.loading p{max-width:500px;text-align:center;color:var(--a-muted);line-height:1.6}
      @media(hover:none){.tile-drag{opacity:.8}.entity-drag{min-width:38px;width:38px}.tile-drag{min-width:38px;min-height:38px}}@media(min-width:1500px){.workspace{padding:26px 32px}.device-stage{max-width:590px}}@media(max-width:1180px){main{padding:22px 18px}.editor-shell{grid-template-columns:minmax(205px,245px) minmax(320px,1fr)}.inspector{grid-column:1/-1;position:static;max-height:none}.inspector form{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.property-group{border-top:0;border-left:1px solid var(--a-border);padding:0 0 0 18px;margin:0}.property-group:first-child{border-left:0;padding-left:0}.property-group:last-child{grid-column:1/-1;display:flex;align-items:end;gap:20px;border-left:0;border-top:1px solid var(--a-border);padding:16px 0 0}.property-group:last-child label{min-width:230px;margin:0}.property-group:last-child .text-button{margin:0}.inspector-placeholder{padding:10px}.inspector-placeholder>ha-icon{display:none}.inspector-placeholder h2{margin:0}.header-actions{gap:8px}.device-picker{min-width:150px}}@media(max-width:760px){main{padding:18px 12px 28px}.app-header{align-items:start;flex-direction:column;gap:18px}.brand-mark{width:44px;height:44px}.brand{gap:13px}h1{font-size:27px}.header-actions{width:100%;justify-content:space-between}.device-picker{flex:1}.save-button{font-size:12px;padding:10px 17px;min-height:45px}.status-row{font-size:10px;gap:9px 14px;padding:12px;border-radius:17px}.editor-shell{display:flex;flex-direction:column;gap:14px}.workspace{order:0;width:100%;padding:17px 14px;border-radius:25px}.library{order:2;width:100%;position:static;max-height:none}.inspector{order:1;width:100%;position:static;border-radius:25px}.inspector form{display:block}.property-group,.property-group:first-child{border:0;border-top:1px solid var(--a-border);padding:17px 0 0;margin-top:8px}.property-group:first-child{border-top:0;padding-top:0}.property-group:last-child{display:block}.property-group:last-child label{min-width:0;margin-bottom:16px}.entity-list{max-height:320px;overflow:auto}.entity-copy strong{font-size:13px}.entity-copy small{font-size:10px}.page-tabs{gap:3px;margin-top:15px}.page-tab{font-size:10px;padding:7px 10px}.reserved-page{font-size:9px;padding:5px 2px}.reserved-page ha-icon{display:none}.workspace-tools h2{font-size:16px}.workspace-bottom{margin-top:16px;gap:8px}.workspace-bottom>div{margin-left:auto}.text-button{font-size:10px}.device-stage{padding:7px;max-width:510px}.modal{padding:24px;border-radius:27px}.modal h2{font-size:23px}.modal-actions{gap:6px}.modal-actions button{font-size:11px;padding:9px 12px}.preview-caption{font-size:10px}.keyboard-hint{font-size:9px}}
      @media(prefers-reduced-motion:reduce){*,*:before{transition:none!important;scroll-behavior:auto!important}}
    `;
  }
}
if (!customElements.get("atmosfera-tile-editor")) customElements.define("atmosfera-tile-editor",AtmosferaTileEditor);
