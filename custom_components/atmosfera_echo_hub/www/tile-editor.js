/* Atmosfera's fixed-profile editor. HA owns validation and persistence; preview never calls entity actions. */
const AEH_TEXT = {
  en: {
    statisticsControl:"Hourly statistics",statisticsHint:"Mean and minimum–maximum for the last 24 completed UTC hours. Gaps are missing aggregates, not zero; this is not a live reading.",statisticsUnavailable:"Connect a Statistics-capable display and choose a loaded arithmetic measurement sensor.",statisticsReview:"Use the dedicated hourly statistics view? The card changes only after confirmation and saving. Recorder remains optional; missing history is shown explicitly.",
    agendaControl:"Open agenda",agendaHint:"Read up to 16 events in the next seven days. Previous and Next only browse the list; no calendar changes are sent.",agendaUnavailable:"Connect a display with Agenda support and choose a loaded calendar.",agendaReview:"Use the dedicated agenda view? The current card changes only after confirmation and saving the layout.",
    cameraCaptionOpen:"Open",cameraCaptionUnavailable:"Unavailable",cameraUnavailable:"Camera unavailable",cameraPreview:"Open camera",cameraPreviewReview:"Use a camera preview?",cameraPreviewHint:"The tile opens the existing Camera view directly. Nothing opens while editing. Save the layout when ready.",cameraPreviewUnavailable:"Connect the display and choose an available camera from its camera list.",cameraPreviewDuration:"Preview duration (seconds)",cameraPreviewConfirm:"Use camera preview",cameraPreviewConfigure:"Configure camera preview",
    contextChanged:"HA state since",contextDateUnknown:"Time unavailable",contextDateInvalid:"Date unavailable",contextDateStale:"Waiting for an updated time",contextRise:"Next sunrise",contextSet:"Next sunset",contextElevation:"Elevation",contextAzimuth:"Azimuth",contextAbove:"Above horizon",contextBelow:"Below horizon",
    contextMonths:["January","February","March","April","May","June","July","August","September","October","November","December"],
    actionPanelLegacyData:"This shortcut contains unsupported parameters or a different service. They cannot be carried into the action view.",actionPanelNoParameters:"This view does not pass script parameters.",
    actionParametersControl:"Script with a Yes/No parameter",actionParametersUnsupported:"This view requires a connected device with script parameters enabled.",actionParametersEntity:"The required Boolean field is unavailable or unsupported. Refresh the catalogue.",actionParametersHint:"Choose Yes or No on the device, then Run. Sending the request does not confirm script completion.",actionParametersReview:"Adds a separate script form. No parameter value is saved in the tile; existing action views are not changed automatically.",actionParametersNoDefault:"No default — choose Yes or No before Run.",actionParametersDefaultYes:"Default: Yes",actionParametersDefaultNo:"Default: No",
    actionPanelOpen:"Open",actionPanelControl:"Open action view",actionPanelUnsupported:"This view requires a connected device with the Action profile.",actionPanelEntity:"Action capabilities or services have changed. Refresh the catalogue.",actionPanelHint:"Opens controls for this action. A successful Home Assistant call does not confirm that a script or physical action has finished.",actionPanelPolicyEdit:"Review automation policies",actionPanelCheckConditions:"Run checks conditions",actionPanelSkipConditions:"Run skips conditions",actionPanelKeepRunning:"Disable does not stop running actions",actionPanelStopRunning:"Disable also requests stopping actions, even if already disabled",actionPanelParameters:"Run is unavailable in this view: parameters are required.",actionPanelMetadata:"Run is unavailable in this view: parameter metadata is missing.",actionPanelRunService:"The Run service is unavailable.",actionPanelLastUnknown:"No last-use data",actionPanelLastInvalid:"Cannot display the last-use date",actionPanelCurrent:"Running or queued",
    mediaPanelControl:"Open external media view",mediaPanelUnsupported:"This view requires a connected device with the external media profile.",mediaPanelEntity:"Media capabilities or services have changed. Refresh the catalogue.",mediaPanelHint:"Controls this Home Assistant media player using its supported controls. The dedicated Atmosfera Player stays available for local playback. Volume changes once on release; reported values keep their source precision.",
    extraLockLocked:"Locked",extraLockUnlocked:"Unlocked",extraLockLocking:"Locking",extraLockUnlocking:"Unlocking",extraLockOpen:"Open",extraLockOpening:"Opening",extraLockJammed:"Jammed",
    infoPanelControl:"Open information view",lockPanelControl:"Open lock view",extraUnsupported:"This view requires a connected device with the matching information or lock profile.",extraEntity:"Panel metadata is unavailable or unsupported for this entity.",extraLoading:"Loading panel data…",extraLoadFailed:"Panel data could not be loaded. Retrying shortly.",extraInfoHint:"Shows observations only. Opening this view never sends a device command.",extraLockHint:"Shows the lock state and, when available, an explicit Lock button. It cannot unlock or open the door.",extraLockPassive:"This lock currently offers observation only; no Lock service is available.",extraReviewTitle:"Use this dedicated view?",extraReviewV2:"This updates the draft to layout v3. The tile will open this view; no service is called and nothing is saved yet.",extraReviewV3:"The tile will open this view. No service is called and nothing is saved yet.",extraConfirm:"Use this view",extraNotice:"Dedicated view selected. Save the layout when ready.",extraPreview:"Panel data preview",extraPreviewNote:"Catalogue observation; the device requests fresh data when opened.",extraTooLong:"The complete value exceeds the display limit. No shortened value is shown.",extraInvalid:"The source does not provide a supported observation.",extraEmpty:"The source contains an empty value.",extraRefreshing:"The source has changed. Waiting for refreshed panel data.",extraNoEvent:"No calendar event is provided.",extraExcerpt:"Description excerpt",extraUpdated:"Updated",extraStart:"Start",extraEnd:"End",extraZone:"Time zone",extraAllDay:"All-day event",extraLocation:"Location",extraDescription:"Description",extraClass:"Device class",
    lightDetailControl:"Open light panel",lightDetailHint:"Opens brightness, power, white temperature and effects supported by this light. Opening sends no command.",climatePanelControl:"Open thermostat and settings",climatePanelHint:"Shows the thermostat and supported climate settings together. Opening sends no command. A device without a single temperature target remains a read-only temperature display.",detailUnsupported:"This view requires compatible firmware and a connected control channel.",detailEntity:"Choose a device with available panel metadata.",detailReviewTitle:"Use the full device view?",detailReviewV2:"This updates the draft to layout v3 and opens the full device view. Nothing is saved yet.",detailReviewV3:"This card will open the full device view. Nothing is saved yet.",detailConfirm:"Use device view",detailNotice:"Device view selected. Save the layout when ready.",detailFacetUnavailable:"Some settings are unavailable. The panel shows the capabilities Home Assistant provides.",
    panelUnsupported:"This panel requires compatible firmware and a connected control channel.",panelEntity:"Choose an available device with supported controls.",panelReviewTitle:"Use the device panel?",panelReviewV2:"This updates the draft to layout v3. The tile will open the device panel. Nothing is saved yet.",panelReviewV3:"The tile will open the device panel. Nothing is saved yet.",panelConfirm:"Use device panel",panelNotice:"Device panel selected. Save the layout when ready.",timerPanelControl:"Open timer",timerPanelHint:"Shows the remaining time, pause, resume and restart controls. Opening does not start the timer.",remotePanelControl:"Open remote",remotePanelHint:"Shows power and the activities supported by this remote. Opening sends no command.",powerPanelControl:"Open switch or outlet",powerPanelHint:"Shows the current state and separate power controls. Opening sends no command.",panelDuration:"Initial duration (seconds, optional)",panelDurationHint:"A starting value for the timer view, from 1 to 86400 seconds. Leave blank to use its current duration. Editing does not start the timer.",
    humidityPanelControl:"Open humidity panel",humidityPanelUnsupported:"The humidity panel requires compatible firmware and a connected control channel.",humidityPanelEntity:"Choose a visible humidifier or dehumidifier with available controls.",humidityPanelHint:"Opens target and measured humidity, power and supported modes. Opening sends no device command.",humidityPanelReviewTitle:"Use the humidity panel?",humidityPanelReviewV2:"This updates the draft to layout v3 and opens the humidity panel. Nothing is saved yet.",humidityPanelReviewV3:"This card will open the humidity panel. Nothing is saved yet.",humidityPanelConfirm:"Use humidity panel",humidityPanelNotice:"Humidity panel selected. Save the layout when ready.",
    robotMowerHint:"Opens the mower view with supported mowing, pause and dock controls. Opening sends no command.",robotAreaUnsupported:"The robot panel is available. This device does not expose a supported room selector.",robotAreaUnmapped:"The robot panel is available. No rooms are mapped to this vacuum in Home Assistant.",robotAreaTooMany:"The robot panel is available. Its room selector supports up to eight mapped rooms; this device has more.",robotAreaLabels:"The robot panel is available. Check the room names: some are too long or ambiguous.",
    robotControl:"Open robot or mower panel",robotUnsupported:"The device panel requires compatible firmware and a connected control channel.",robotEntity:"Choose an available vacuum or mower with supported controls.",robotHint:"Opens a dedicated device view with supported actions, suction and mapped rooms. Opening sends no command.",robotReviewTitle:"Use the device panel?",robotReviewV2:"This updates the draft to layout v3 and opens the device panel. Nothing is saved yet.",robotReviewV3:"This card will open the device panel. Nothing is saved yet.",robotConfirm:"Use device panel",robotNotice:"Device panel selected. Save the layout when ready.",
    fanControl:"Open fan panel",fanUnsupported:"The fan panel requires compatible firmware and a connected control channel.",fanEntity:"Choose a visible fan card with available controls.",fanHint:"Opens power, speed, preset, oscillation and direction together. Only supported controls are shown. Opening sends no device command.",fanReviewTitle:"Use the fan panel?",fanReviewV2:"This updates the draft to layout v3. This card will open the fan panel. Nothing is saved yet.",fanReviewV3:"This card will open the fan panel. Nothing is saved yet.",fanConfirm:"Use fan panel",fanNotice:"Fan panel selected. Save the layout when ready.",
    coverPanelControl:"Open cover panel",coverPanelEntity:"Choose an available cover with supported position, tilt or movement controls.",coverPanelHint:"Opens position and tilt in separate sections. Each Stop acts on its own section. Only supported controls are shown; opening sends no command.",coverPanelReviewTitle:"Use the cover panel?",coverPanelReviewV2:"This updates the draft to layout v3 and opens the cover panel. Nothing is saved yet.",coverPanelReviewV3:"This card will open the cover panel. Nothing is saved yet.",coverPanelConfirm:"Use cover panel",coverPanelNotice:"Cover panel selected. Save the layout when ready.",
    coverControl:"Open cover controls",coverUnsupported:"Cover controls require compatible firmware and a connected control channel.",coverEntity:"Choose a visible Entity card for an available Cover with supported Open, Stop or Close actions.",coverHint:"Opens separate Open, Stop and Close controls. Only supported actions are enabled. Preview sends no command.",coverReviewTitle:"Use cover controls?",coverReviewV2:"This changes the draft to layout v3 and opens cover controls for this card. Other cards are preserved. Nothing is saved yet.",coverReviewV3:"This card will open cover controls. Nothing is saved yet.",coverConfirm:"Use cover controls",coverNotice:"Cover controls selected in the draft. Save when ready.",hiddenText:"Hidden text",stateLabels:"State descriptions",stateLabelsHint:"Replace exact source states with short descriptions on this information card. Unmatched states keep Home Assistant formatting. Unknown and unavailable cannot be renamed.",stateLabelsKey:"Source state",stateLabelsValue:"Display text",stateLabelsAdd:"Add description",stateLabelsRemove:"Remove description",stateLabelsApply:"Use descriptions",stateLabelsInvalid:"Use distinct source states and non-empty printable text, up to 32 UTF-8 bytes per field and eight descriptions. Unknown and unavailable are reserved.",stateLabelsChanged:"The card or draft changed. Open its descriptions again.",stateLabelsNotice:"State descriptions changed in the draft. Save when ready.",
    tileEventPanel:"Event panel",tileEventPanelCreate:"Add event panel",tileEventPanelReview:"Use an event panel?",tileEventPanelHint:"The tile opens a dedicated view. Only its Send event button triggers the Home Assistant event. Preview and opening send nothing.",tileEventPanelConfirm:"Use event panel",tileEventPanelUnavailable:"A connected display with Action and event panel support is required.",tileEventTitle:"Automation",tileEvent:"Automation button",tileEventCreate:"Add automation button",tileEventHint:"Each press is available as an event in Home Assistant. Create an automation there to choose what happens. Preview sends nothing.",tileEventReview:"Use an automation button?",tileEventReviewHint:"This replaces the card's entity and tap action with an automation button. Its title and style stay the same. Nothing is saved yet.",tileEventEmptyHint:"Create a button, then use its event in a Home Assistant automation. Nothing is saved yet.",tileEventConfirm:"Use automation button",tileEventChanged:"The card, display or connection changed. Open a new review.",tileEventUnavailable:"Automation buttons require a connected display with compatible touch reports.",tileEventNotice:"Automation button added to the draft. Save when ready.",
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
    effectControl:"Choose light effect",effectUnsupported:"Effect selection requires a connected compatible display.",effectEntity:"Choose an available light with a short, distinct effect list and a known current effect or known empty selection.",effectHint:"Choose an effect, then Apply. This starts the effect and can turn the light on.",effectReviewTitle:"Use light effect selection?",effectReviewV2:"This changes the draft to layout v3 and opens effect selection. Applying an effect can turn the light on. Other cards are preserved. Nothing is saved yet.",effectReviewV3:"This card will open effect selection. Applying an effect can turn the light on. Nothing is saved yet.",effectConfirm:"Use light effects",effectNotice:"Light effect selection added to the draft. Save when ready.",effectEmpty:"No effect",
    humiModeControl:"Choose operating mode",humiModeUnsupported:"Operating modes require compatible firmware and a connected choice channel.",humiModeEntity:"Choose an available humidifier or dehumidifier with mode support and a short, distinct mode list.",humiModeHint:"Choose the humidifier or dehumidifier mode on the display, then Apply.",humiModeReviewTitle:"Use device mode selection?",humiModeReviewV2:"This changes the draft to layout v3 and opens device mode selection. Other cards are preserved. Nothing is saved yet.",humiModeReviewV3:"This card will open device mode selection. Nothing is saved yet.",humiModeConfirm:"Use mode selection",humiModeNotice:"Device mode selection added to the draft. Save when ready.",humiModeNormal:"Normal",humiModeEco:"Eco",humiModeAway:"Away",humiModeBoost:"Boost",humiModeComfort:"Comfort",humiModeHome:"Home",humiModeSleep:"Sleep",humiModeAuto:"Automatic",humiModeBaby:"Baby",
    humidifierPowerHint:"Tap the display tile to switch the humidifier or dehumidifier on or off.",humidifierPowerUnavailable:"Power control is unavailable. Check the connection and device state.",humidifierOn:"On",humidifierOff:"Off",
    horizontalControl:"Choose horizontal swing",horizontalUnsupported:"Horizontal swing requires compatible firmware and a connected choice channel.",horizontalEntity:"Choose an available climate with independent horizontal swing and a short, distinct mode list.",horizontalHint:"Choose the horizontal louvre movement on the display, then Apply.",horizontalReviewTitle:"Use horizontal swing selection?",horizontalReviewV2:"This changes the draft to layout v3 and opens horizontal swing selection. Other cards are preserved. Nothing is saved yet.",horizontalReviewV3:"This card will open horizontal swing selection. Nothing is saved yet.",horizontalConfirm:"Use horizontal swing",horizontalNotice:"Horizontal swing selection added to the draft. Save when ready.",horizontalOff:"Off",horizontalOn:"On",
    swingControl:"Choose climate swing mode",swingUnsupported:"Swing mode requires compatible firmware and a connected choice channel.",swingEntity:"Choose an available climate with swing support and a short, distinct mode list.",swingHint:"Choose the louvre movement on the display, then Apply.",swingReviewTitle:"Use climate swing selection?",swingReviewV2:"This changes the draft to layout v3 and opens climate swing selection. Other cards are preserved. Nothing is saved yet.",swingReviewV3:"This card will open climate swing selection. Nothing is saved yet.",swingConfirm:"Use swing selection",swingNotice:"Climate swing selection added to the draft. Save when ready.",swingOff:"Off",swingOn:"On",swingVertical:"Vertical",swingHorizontal:"Horizontal",swingBoth:"Both axes",
    airflowControl:"Choose climate fan mode",airflowUnsupported:"Fan mode requires compatible firmware and a connected choice channel.",airflowEntity:"Choose an available climate with fan mode support and a short, distinct fan mode list.",airflowHint:"Choose the fan mode on the display, then Apply.",airflowReviewTitle:"Use climate fan mode selection?",airflowReviewV2:"This changes the draft to layout v3 and opens climate fan mode selection. Other cards are preserved. Nothing is saved yet.",airflowReviewV3:"This card will open climate fan mode selection. Nothing is saved yet.",airflowConfirm:"Use fan mode selection",airflowNotice:"Climate fan mode selection added to the draft. Save when ready.",airflowAuto:"Automatic",airflowLow:"Low",airflowMedium:"Medium",airflowHigh:"High",airflowOn:"On",airflowOff:"Off",airflowTop:"Top",airflowMiddle:"Middle",airflowFocus:"Focused",airflowDiffuse:"Diffuse",
    presetControl:"Choose climate program",presetUnsupported:"Climate programs require compatible firmware and a connected choice channel.",presetEntity:"Choose an available climate with preset support and a short, distinct program list.",presetHint:"Choose a program on the display, then Apply. A program may change the device settings.",presetReviewTitle:"Use climate program selection?",presetReviewV2:"This changes the draft to layout v3 and opens climate program selection. Other cards are preserved. Nothing is saved yet.",presetReviewV3:"This card will open climate program selection. Nothing is saved yet.",presetConfirm:"Use climate programs",presetNotice:"Program selection added to the draft. Save when ready.",presetNone:"No program",presetEco:"Eco",presetComfort:"Comfort",presetSleep:"Sleep",presetAway:"Away",presetHome:"Home",presetBoost:"Boost",presetActivity:"Activity",
    hvacControl:"Choose operating mode",hvacUnsupported:"Operating modes require compatible firmware and a connected choice channel.",hvacEntity:"Choose an available climate with a known mode and a short, distinct mode list.",hvacHint:"Choose a supported mode on the display, then Apply. Target temperature is configured separately.",hvacReviewTitle:"Use operating mode selection?",hvacReviewV2:"This changes the draft to layout v3 and opens operating mode selection. Other cards are preserved. Nothing is saved yet.",hvacReviewV3:"This card will open operating mode selection. Nothing is saved yet.",hvacConfirm:"Use operating modes",hvacNotice:"Operating mode selection added to the draft. Save when ready.",hvacOff:"Off",hvacHeat:"Heating",hvacCool:"Cooling",hvacHeatCool:"Heat/cool",hvacAuto:"Automatic",hvacDry:"Drying",hvacFanOnly:"Fan only",
    coverTiltControl:"Adjust slat tilt",coverTiltUnsupported:"Slat tilt adjustment requires a connected compatible display.",coverTiltEntity:"Choose an available cover with tilt position support and a reported current slat tilt.",coverTiltHint:"Each +/− changes slat tilt by 1 percentage point in Home Assistant's 0–100% range. Raising/lowering the cover and Stop tilt are separate actions. Closing this screen does not stop movement.",coverTiltReviewTitle:"Use slat tilt adjustment?",coverTiltReviewV2:"The draft will use layout v3 and this card will open precise slat tilt adjustment. Other cards are preserved. Nothing is saved yet.",coverTiltReviewV3:"This card will open precise slat tilt adjustment, independently of the cover opening percentage. Nothing is saved yet.",coverTiltConfirm:"Use slat tilt adjustment",coverTiltNotice:"Slat tilt adjustment added to the draft. Save when ready.",coverTiltValue:"Tilt",
    coverPositionControl:"Adjust opening percentage",coverPositionUnsupported:"Opening adjustment requires a connected compatible display.",coverPositionEntity:"Choose an available cover that supports position control and reports its current opening percentage.",coverPositionHint:"Each +/− changes opening by 1 percentage point: 0% closed, 100% open. Closing this screen does not stop movement; Stop is a separate cover action.",coverPositionReviewTitle:"Use opening adjustment?",coverPositionReviewV2:"The draft will use layout v3 and this card will open precise cover position adjustment. Other cards are preserved. Nothing is saved yet.",coverPositionReviewV3:"This card will open precise cover position adjustment. Opening, closing and Stop remain separate actions. Nothing is saved yet.",coverPositionConfirm:"Use opening adjustment",coverPositionNotice:"Cover position adjustment added to the draft. Save when ready.",coverOpening:"Opening",
    vacuumPowerControl:"Choose vacuum power",vacuumPowerUnsupported:"Vacuum power selection requires a connected compatible display.",vacuumPowerEntity:"Choose an available vacuum with a known power level and a short, distinct list of supported levels.",vacuumPowerHint:"Choose a supported suction level, then Apply. Starting cleaning and returning to the dock are separate actions.",vacuumPowerReviewTitle:"Use vacuum power selection?",vacuumPowerReviewV2:"This changes the draft to layout v3 and opens vacuum power selection. Other cards are preserved. Nothing is saved yet.",vacuumPowerReviewV3:"This card will open vacuum power selection. Cleaning and docking remain separate actions. Nothing is saved yet.",vacuumPowerConfirm:"Use vacuum power",vacuumPowerNotice:"Vacuum power selection added to the draft. Save when ready.",vacuumQuiet:"Quiet",vacuumSilent:"Silent",vacuumNormal:"Normal",vacuumStandard:"Standard",vacuumTurbo:"Turbo",vacuumEco:"Eco",vacuumMax:"Maximum",vacuumStrong:"Strong",vacuumGentle:"Gentle",vacuumOff:"Off",
    speedControl:"Choose fan speed",speedUnsupported:"Fan speeds require compatible firmware and a connected choice channel.",speedEntity:"Choose an available fan with 1 to 7 declared speeds, matching percentage step and a known speed.",speedHint:"Choose a supported speed, then Apply. Changing speed can start or stop the fan, depending on its integration.",speedReviewTitle:"Use fan speed selection?",speedReviewV2:"This changes the draft to layout v3 and opens fan speed selection. Changing speed can start or stop the fan. Other cards are preserved. Nothing is saved yet.",speedReviewV3:"This card will open fan speed selection. Changing speed can start or stop the fan. Nothing is saved yet.",speedConfirm:"Use fan speeds",speedNotice:"Fan speed selection added to the draft. Save when ready.",
    kelvinControl:"Fine-tune color temperature",kelvinUnsupported:"Color temperature needs compatible firmware and a connected number channel.",kelvinEntity:"Choose an on light in color-temperature mode with a known integer Kelvin value and exact supported range.",kelvinHint:"Fine adjustment by 1 K while color-temperature mode is active. Power and other color modes are controlled separately.",kelvinReviewTitle:"Use precise color temperature controls?",kelvinReviewV2:"This changes the draft to layout v3 and opens fine adjustment by 1 K. Other cards are preserved. Nothing is saved yet.",kelvinReviewV3:"This card will open fine adjustment by 1 K while the light is on in color-temperature mode. Nothing is saved yet.",kelvinConfirm:"Use precise color temperature",kelvinNotice:"Color temperature controls added to the draft. Save when ready.",
    climateHumidityControl:"Adjust climate target humidity",climateHumidityUnsupported:"Climate humidity needs compatible firmware and a connected number channel.",climateHumidityEntity:"Choose an available climate with supported target humidity, a known target and an exact integer range and step.",climateHumidityHint:"Adjusts target humidity by its supported step. HVAC mode and target temperature have separate controls.",climateHumidityReviewTitle:"Use climate humidity controls?",climateHumidityReviewV2:"This changes the draft to layout v3 and opens climate target humidity. Other cards are preserved. Nothing is saved yet.",climateHumidityReviewV3:"This card will open climate target humidity. HVAC mode and target temperature remain separate. Nothing is saved yet.",climateHumidityConfirm:"Use climate target humidity",climateHumidityNotice:"Climate humidity controls added to the draft. Save when ready.",
    humidityControl:"Adjust target humidity",humidityUnsupported:"Humidity adjustment requires compatible firmware and a connected number channel.",humidityEntity:"Choose an available humidifier with a known target and exact integer range and step.",humidityHint:"Adjusts the target humidity by the supported step. Power and operating mode stay unchanged.",humidityReviewTitle:"Use target humidity controls?",humidityReviewV2:"This changes the draft to layout v3 and opens target humidity controls. Other cards are preserved. Nothing is saved yet.",humidityReviewV3:"This card will open target humidity controls. Nothing is saved yet.",humidityConfirm:"Use target humidity",humidityNotice:"Target humidity controls added to the draft. Save when ready.",
    thermostatReadOnly:"Opens the thermostat in view-only mode. The provider has no confirmed adjustable target.",temperatureControl:"Open thermostat",temperatureTarget:"Target",temperatureUnsupported:"Target adjustment requires compatible firmware and a connected number channel.",temperatureEntity:"Choose an available single-target climate with an exact range, step and matching temperature unit.",temperatureHint:"Adjusts one target by the supported step. HVAC mode stays unchanged. Unknown values cannot be changed.",temperatureReviewTitle:"Use target temperature controls?",temperatureReviewV2:"This changes the draft to layout v3 and opens target temperature controls. Other cards are preserved. Nothing is saved yet.",temperatureReviewV3:"This card will open target temperature controls. Nothing is saved yet.",temperatureConfirm:"Use target temperature",temperatureNotice:"Target temperature controls added to the draft. Save when ready.",
    directionControl:"Choose fan direction",directionForward:"Forward",directionReverse:"Reverse",directionUnsupported:"Fan direction requires compatible firmware and a connected choice channel.",directionEntity:"Choose an available fan with a known direction and direction control.",directionHint:"Choose Forward or Reverse on the display, then Apply. Fan power stays unchanged.",directionReviewTitle:"Use fan direction selection?",directionReviewV2:"This changes the draft to layout v3 and opens fan direction selection. Other cards are preserved. Nothing is saved yet.",directionReviewV3:"This card will open fan direction selection. Nothing is saved yet.",directionConfirm:"Use direction selection",directionNotice:"Direction selection added to the draft. Save when ready.",
    fanManual:"Manual mode",fanOscillation:"Toggle oscillation",fanOscillationOn:"Oscillation: on",fanOscillationOff:"Oscillation: off",fanOscillationHint:"Toggles the observed oscillation state. Fan power stays unchanged. Preview sends no command.",
    calendarPlacement:"Calendar events use the wide information row on Security.",calendarHint:"Shows the event reported by Home Assistant: date, time and a short title. This is not a full agenda; tapping sends no command.",
    personPlacement:"Person zone names use the wide information row on Security.",personHint:"Shows the presence or zone reported by Home Assistant. Color follows the exact Home state. Tapping sends no command; photos and maps are separate features.",
    vacuumRoom:"Clean a room",vacuumRoomChoose:"Choose a mapped room",vacuumRoomUnavailable:"Selected room is unavailable",vacuumRoomHint:"Choose an area already mapped in the vacuum settings in Home Assistant. This only edits the draft. The robot must be docked, idle or paused to start.",vacuumRoomMissing:"No mapped rooms available. Configure area mapping in the vacuum entity settings in Home Assistant, then refresh.",vacuumRoomRefresh:"Refresh rooms",
    vacuumStart:"Start / resume cleaning",vacuumPause:"Pause cleaning",vacuumStop:"Stop cleaning",vacuumDock:"Return to dock",vacuumLocate:"Locate robot",vacuumSpot:"Clean current spot",vacuumActionsHint:"Choose what tapping this card will do. These buttons only edit the layout. The card follows the reported activity; commands never simulate feedback. Suction level is configured separately.",
    mediaStop:"Stop playback",mediaStatePrefix:"State: ",mediaStopHint:"Assign this tile to stop playback on the selected player. It becomes active during playback, buffering or pause.",
    mediaVolumeTarget:"Set volume",mediaVolumePercent:"Target volume (%)",mediaVolumeTargetHint:"Set the volume this tile will request, from 0 to 100%. The tile shows reported volume. Editing the draft does not change the player. This configures a fixed target; it does not add a slider to the display.",
    mediaLouder:"Louder",mediaQuieter:"Quieter",mediaVolumeHint:"Choose Louder or Quieter for the tile. Each tap changes volume by the player’s own step. The preview shows reported volume; these buttons only edit the draft.",
    mediaShuffle:"Shuffle",mediaUnshuffle:"In order",mediaShuffleField:"Shuffle playback",mediaShuffleService:"Shuffle playback",mediaShuffled:"Shuffle on",mediaInOrder:"In order",mediaShuffleHint:"Choose the tile action. These buttons change only the draft. Shuffle follows the reported player state and preserves playback, volume and repeat.",
    mediaRepeatControl:"Choose repeat mode",mediaRepeatUnsupported:"Repeat requires compatible, connected choice controls.",mediaRepeatEntity:"Choose a player supporting repeat with a known current mode.",mediaRepeatHint:"Choose repeat mode on the display, then Apply. Playback, track and volume are preserved.",mediaRepeatReviewTitle:"Use repeat selection?",mediaRepeatReviewV2:"This changes the draft to layout v3 and opens repeat selection. Other cards are preserved. Nothing is saved yet.",mediaRepeatReviewV3:"This card will open repeat selection. Nothing is saved yet.",mediaRepeatConfirm:"Use repeat selection",mediaRepeatNotice:"Repeat selection added to the draft. Save when ready.",mediaRepeatPrefix:"Repeat: ",repeatOff:"Off",repeatOne:"One track",repeatAll:"All tracks",
    mediaSoundPrefix:"Sound: ",mediaSoundControl:"Choose sound mode",mediaSoundUnsupported:"Sound modes require compatible, connected choice controls.",mediaSoundEntity:"Choose an available player with a known mode and a short list of distinct sound modes.",mediaSoundHint:"Choose a sound mode on the display, then Apply. It changes audio processing in the selected player; it does not send Play, Power or Volume commands.",mediaSoundReviewTitle:"Use sound mode selection?",mediaSoundReviewV2:"This changes the draft to layout v3 and opens sound mode selection. Other cards are preserved. Nothing is saved yet.",mediaSoundReviewV3:"This card will open sound mode selection. Nothing is saved yet.",mediaSoundConfirm:"Use sound mode selection",mediaSoundNotice:"Sound mode selection added to the draft. Save when ready.",
    mediaSourceControl:"Choose player source",mediaSourceUnsupported:"Source selection requires compatible, connected choice controls.",mediaSourceEntity:"Choose an available player with a known source and a short list of distinct inputs.",mediaSourceHint:"Choose a source on the display, then Apply. This does not send Play, Power or Volume commands.",mediaSourceReviewTitle:"Use source selection?",mediaSourceReviewV2:"This changes the draft to layout v3 and opens source selection. Other cards are preserved. Nothing is saved yet.",mediaSourceReviewV3:"This card will open source selection. Nothing is saved yet.",mediaSourceConfirm:"Use source selection",mediaSourceNotice:"Source selection added to the draft. Save when ready.",
    activityControl:"Choose remote activity",activityUnsupported:"Activity selection requires compatible, connected choice controls.",activityEntity:"Choose an available remote with activity support and a short list of distinct activities.",activityHint:"Choose an activity on the display, then Apply. Power status remains the Home summary.",activityReviewTitle:"Use activity selection?",activityReviewV2:"This changes the draft to layout v3 and opens activity selection. Other cards are preserved. Nothing is saved yet.",activityReviewV3:"This card will open activity selection. Nothing is saved yet.",activityConfirm:"Use activity selection",activityNotice:"Activity selection added to the draft. Save when ready.",
    mediaMute:"Mute",mediaUnmute:"Restore sound",mediaMuteField:"Mute sound",mediaMuteService:"Player mute",mediaMuted:"Muted",mediaSoundOn:"Sound on",mediaOff:"Off",mediaMuteHint:"Choose what tapping this tile will do. These buttons only edit the draft. Mute follows the player’s reported state and leaves playback, track and volume unchanged.",
    remoteOn:"Turn remote on",remoteOff:"Turn remote off",remoteHint:"Choose the explicit power command for this tile. These buttons only edit the draft. The tile follows the state reported by Home Assistant; an already completed transition is disabled. Activities and learned commands are configured separately.",
    mowerStart:"Start / resume mowing",mowerPause:"Pause mowing",mowerDock:"Return to dock",mowerHint:"Choose what tapping this card will do. These buttons only edit the layout. Start also resumes a paused task. The card is disabled when the current activity or capabilities do not allow its command.",
    textPanelControl:"Open text editor",textPanelUnsupported:"This view requires a connected device with the text profile.",textPanelEntity:"Text panel data is unavailable or unsupported.",textPanelHint:"Edit a local draft, then Save its complete value to Home Assistant.",textPanelPassive:"This helper currently provides a read-only view.",textPanelReview:"Use an entity tile that opens the text editor. Sensor-only formatting will be removed. This changes only the layout draft; Save the layout separately. No text is sent.",textPanelHidden:"Text hidden",textPanelPattern:"Editing patterned text is not supported.",textPanelBounds:"Text length limits are unsupported.",textPanelLength:"The current text exceeds the supported length limits.",textPanelCharacters:"The current text contains unsupported characters.",textPanelEmpty:"Empty text",
    datetimePanelControl:"Open date and time editor",datetimePanelUnsupported:"This view requires a connected device with the date and time profile.",datetimePanelEntity:"Date and time panel data is unavailable or unsupported.",datetimePanelHint:"Edit a local draft on the device, then use Save to send one complete value to Home Assistant.",datetimePanelPassive:"This helper currently supports observation only; the date and time service is unavailable.",datetimePanelReview:"Use an entity tile that opens the date and time editor. Sensor-only formatting will be removed. This changes the draft to layout v3; no value is sent and nothing is saved yet.",datetimePanelWallHint:"The helper stores a calendar date and/or local clock value. It does not select a UTC instant or a repeated-hour occurrence.",
    datetimePlacement:"Date and time information needs a wide text tile.",
    entity:"Entity",changeEntity:"Choose an entity from the library",title:"Title",icon:"Icon",palette:"Color",visible:"Show on screen",
    type:"Card type",entityType:"Entity",sensorType:"Information",actionType:"Action",tap:"On tap",default:"Default action",none:"Do nothing",
    service:"Configured action",chooseService:"Choose an action",noActions:"No supported action is available for this entity.",
    actionUnavailable:"This saved action is currently unavailable. Choose a supported action before saving.",
    controlProfileChanged:"The display profile changed. Reload the saved layout before choosing light controls.",
    numberControl:"Open Number stepper",numberUnsupported:"Number controls require matching firmware and a negotiated generic control channel.",numberEntity:"Choose a visible Entity card for an available Number entity or helper with an exact supported numeric domain.",numberHint:"Opens minus/plus controls. The preview sends no commands; Home Assistant rechecks the current value and step metadata.",numberReviewTitle:"Use Number controls?",numberReviewV2:"This changes the draft to layout v3 and opens Number controls for this card. Other cards are preserved. Nothing is saved yet.",numberReviewV3:"This card will open Number controls. Nothing is saved yet.",numberConfirm:"Use Number controls",numberNotice:"Number controls selected in the draft. Save the layout when ready.",
    control:"Open light controls",controlHint:"Opens the device's light controls. The preview never sends commands; On/Off and brightness are validated again by Home Assistant.",controlUnsupported:"Light controls require matching firmware and a connected, negotiated light-control channel. Existing tap actions are unchanged.",controlEntity:"Choose a visible Entity card for an available light with a supported power action.",controlBrightness:"Brightness is available when the light supports it. An unknown value is shown as --, never an invented percentage.",controlPowerOnly:"Brightness unavailable. Only the light's supported On/Off actions will be enabled.",controlReviewTitle:"Use light controls?",controlReviewV2:"This changes the draft to layout v3 and makes this card open light controls. All other card IDs, positions and actions are preserved. Older firmware keeps this card passive. Nothing is saved yet.",controlReviewV3:"This card will open light controls. Nothing is saved yet; review the draft and save when ready.",controlConfirm:"Use light controls",controlChanged:"The display, draft or light capability changed. Review the current card and try again.",controlNotice:"Light controls selected in the draft. Save the layout when ready.",
    parameters:"Action settings",optional:"Optional",required:"Required",true:"Yes",false:"No",rgb:"Red, green, blue (0–255)",
    timerDuration:"Duration (seconds)",timerDurationHint:"Set 1–86400 seconds for a preset. Leave empty to keep the timer's remaining time when resuming.",
    stateColor:"Highlight the active state",stateColorHint:"Use the selected palette when on, open or detected, and a quiet surface when off or unavailable.",
    precision:"Decimal places",precisionAuto:"From Home Assistant",precisionHint:"Only this numeric information card changes. Dates, descriptions and durations keep their existing format.",outOfRange:"Out of range",
    autoIcon:"From sensor type",
    presencePresent:"Present",presenceAway:"Away",
    automationEnable:"Enable",automationDisable:"Disable",automationRun:"Run",
    automationHint:"The default tap enables or disables future triggers. A running sequence is allowed to finish. Choose Run separately to execute actions.",
    automationRunHint:"Run executes the automation once. Skip conditions: Yes or empty ignores its conditions; No checks them.",
    automationOffHint:"Stop running actions: Yes or empty stops a current run; No lets it finish.",
    skipConditions:"Skip conditions",stopActions:"Stop running actions",
    choiceControl:"Open option selection",choiceUnsupported:"Option selection requires compatible firmware and a connected control channel.",choiceEntity:"Choose a visible Entity card for an available Select or fan preset with one to eight short, distinct options.",choiceHint:"Choose an option on the display, then Apply. Choosing in the preview sends no command.",choiceReviewTitle:"Use option selection?",choiceReviewV2:"This changes the draft to layout v3 and opens option selection for this card. Other cards are preserved. Nothing is saved yet.",choiceReviewV3:"This card will open option selection. Nothing is saved yet.",choiceConfirm:"Use option selection",choiceNotice:"Option selection added to the draft. Save when ready.",
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
    statisticsControl:"Statystyki godzinowe",statisticsHint:"Średnia oraz minimum–maksimum z ostatnich 24 zakończonych godzin UTC. Luki oznaczają brak agregatu, nie zero; to nie jest bieżący pomiar.",statisticsUnavailable:"Połącz ekran z obsługą statystyk i wybierz załadowany czujnik pomiarowy.",statisticsReview:"Użyć dedykowanego widoku statystyk godzinowych? Kafelek zmieni się dopiero po potwierdzeniu i zapisaniu. Recorder pozostaje opcjonalny; brak historii zostanie wyraźnie pokazany.",
    agendaControl:"Otwórz agendę",agendaHint:"Odczyt maksymalnie 16 wydarzeń z najbliższych siedmiu dni. Poprzednie i Następne służą tylko do przeglądania listy; kalendarz pozostaje bez zmian.",agendaUnavailable:"Połącz ekran z obsługą Agendy i wybierz załadowany kalendarz.",agendaReview:"Użyć dedykowanego widoku agendy? Kafelek zmieni się dopiero po potwierdzeniu i zapisaniu układu.",
    cameraCaptionOpen:"Otwórz",cameraCaptionUnavailable:"Niedostępna",cameraUnavailable:"Kamera niedostępna",cameraPreview:"Otwórz kamerę",cameraPreviewReview:"Użyć podglądu kamery?",cameraPreviewHint:"Kafelek otwiera bezpośrednio istniejący widok Kamera. Edycja niczego nie otwiera. Zapisz gotowy układ.",cameraPreviewUnavailable:"Połącz ekran i wybierz dostępną kamerę z jego listy kamer.",cameraPreviewDuration:"Czas podglądu (sekundy)",cameraPreviewConfirm:"Użyj podglądu kamery",cameraPreviewConfigure:"Skonfiguruj podgląd kamery",
    contextChanged:"Stan HA od",contextDateUnknown:"Brak danych o czasie",contextDateInvalid:"Nie można odczytać daty",contextDateStale:"Oczekiwanie na aktualny termin",contextRise:"Najbliższy wschód",contextSet:"Najbliższy zachód",contextElevation:"Wysokość",contextAzimuth:"Azymut",contextAbove:"Nad horyzontem",contextBelow:"Pod horyzontem",
    contextMonths:["stycznia","lutego","marca","kwietnia","maja","czerwca","lipca","sierpnia","września","października","listopada","grudnia"],
    actionPanelLegacyData:"Ten skrót zawiera nieobsługiwane parametry lub inną usługę. Nie można ich przenieść do widoku akcji.",actionPanelNoParameters:"Ten widok nie przekazuje parametrów skryptu.",
    actionParametersControl:"Skrypt z parametrem Tak/Nie",actionParametersUnsupported:"Ten widok wymaga połączonego urządzenia z obsługą parametrów skryptów.",actionParametersEntity:"Wymagane pole logiczne jest niedostępne lub nieobsługiwane. Odśwież katalog.",actionParametersHint:"Na urządzeniu wybierz Tak lub Nie, a następnie Uruchom. Wysłanie żądania nie potwierdza zakończenia skryptu.",actionParametersReview:"Dodaje osobny formularz skryptu. W kafelku nie zapisujemy wartości parametru; dotychczasowe widoki akcji pozostają bez zmian.",actionParametersNoDefault:"Brak wartości domyślnej — przed uruchomieniem wybierz Tak lub Nie.",actionParametersDefaultYes:"Domyślnie: Tak",actionParametersDefaultNo:"Domyślnie: Nie",
    actionPanelOpen:"Otwórz",actionPanelControl:"Otwórz widok akcji",actionPanelUnsupported:"Ten widok wymaga połączonego urządzenia z profilem akcji.",actionPanelEntity:"Możliwości akcji lub usługi zmieniły się. Odśwież katalog.",actionPanelHint:"Otwiera sterowanie tą akcją. Przyjęcie wywołania przez Home Assistant nie potwierdza zakończenia skryptu ani działania urządzenia.",actionPanelPolicyEdit:"Sprawdź zasady automatyzacji",actionPanelCheckConditions:"Uruchom sprawdza warunki",actionPanelSkipConditions:"Uruchom pomija warunki",actionPanelKeepRunning:"Wyłączenie nie zatrzymuje trwających działań",actionPanelStopRunning:"Wyłączenie również zleca zatrzymanie działań, także gdy automatyzacja jest już wyłączona",actionPanelParameters:"Uruchomienie w tym widoku jest niedostępne: wymagane są parametry.",actionPanelMetadata:"Uruchomienie w tym widoku jest niedostępne: brak danych o parametrach.",actionPanelRunService:"Usługa uruchamiania jest niedostępna.",actionPanelLastUnknown:"Brak danych o ostatnim użyciu",actionPanelLastInvalid:"Nie można wyświetlić daty ostatniego użycia",actionPanelCurrent:"Wykonania i kolejka",
    mediaPanelControl:"Otwórz widok zewnętrznych mediów",mediaPanelUnsupported:"Ten widok wymaga połączonego urządzenia z profilem zewnętrznych mediów.",mediaPanelEntity:"Możliwości odtwarzacza lub usługi zmieniły się. Odśwież katalog.",mediaPanelHint:"Steruje tą encją multimedialną Home Assistant zgodnie z jej możliwościami. Dedykowany Player Atmosfery nadal służy do lokalnego odtwarzania. Głośność zmienia się raz po puszczeniu; odczyty zachowują dokładność źródła.",
    extraLockLocked:"Zaryglowany",extraLockUnlocked:"Odryglowany",extraLockLocking:"Ryglowanie",extraLockUnlocking:"Odryglowywanie",extraLockOpen:"Otwarte",extraLockOpening:"Otwieranie",extraLockJammed:"Zablokowany mechanizm",
    infoPanelControl:"Otwórz widok informacyjny",lockPanelControl:"Otwórz widok zamka",extraUnsupported:"Ten widok wymaga połączonego urządzenia z obsługą odpowiedniego profilu informacji lub zamka.",extraEntity:"Metadane widoku tej encji są niedostępne lub nieobsługiwane.",extraLoading:"Pobieranie danych widoku…",extraLoadFailed:"Nie udało się pobrać danych widoku. Wkrótce ponowimy próbę.",extraInfoHint:"Pokazuje wyłącznie obserwacje. Otwarcie widoku nigdy nie wysyła polecenia do urządzenia.",extraLockHint:"Pokazuje stan zamka i, jeśli jest dostępny, przycisk Zarygluj. Nie może odryglować ani otworzyć drzwi.",extraLockPassive:"Ten zamek udostępnia teraz tylko podgląd; usługa ryglowania jest niedostępna.",extraReviewTitle:"Użyć dedykowanego widoku?",extraReviewV2:"Szkic zostanie zaktualizowany do układu v3. Kafelek otworzy ten widok; żadna usługa nie zostanie wywołana i nic nie jest jeszcze zapisane.",extraReviewV3:"Kafelek otworzy ten widok. Żadna usługa nie zostanie wywołana i nic nie jest jeszcze zapisane.",extraConfirm:"Użyj widoku",extraNotice:"Wybrano dedykowany widok. Zapisz układ, gdy będzie gotowy.",extraPreview:"Podgląd danych widoku",extraPreviewNote:"Obserwacja z katalogu. Urządzenie pobiera świeże dane przy otwarciu widoku.",extraTooLong:"Pełna wartość przekracza limit wyświetlania. Nie pokazujemy skróconego odczytu.",extraInvalid:"Źródło nie udostępnia obsługiwanego odczytu.",extraEmpty:"Źródło zawiera pustą wartość.",extraRefreshing:"Źródło zmieniło się. Oczekiwanie na odświeżone dane widoku.",extraNoEvent:"Brak zdarzenia w kalendarzu.",extraExcerpt:"Fragment opisu",extraUpdated:"Aktualizacja",extraStart:"Początek",extraEnd:"Koniec",extraZone:"Strefa czasowa",extraAllDay:"Wydarzenie całodniowe",extraLocation:"Miejsce",extraDescription:"Opis",extraClass:"Klasa urządzenia",
    lightDetailControl:"Otwórz panel światła",lightDetailHint:"Otwiera jasność, zasilanie, barwę bieli i efekty obsługiwane przez to światło. Samo otwarcie nie wysyła polecenia.",climatePanelControl:"Otwórz termostat i ustawienia",climatePanelHint:"Pokazuje termostat i obsługiwane ustawienia klimatu razem. Samo otwarcie nie wysyła polecenia. Urządzenie bez pojedynczej temperatury zadanej nadal pokazuje jej odczyt.",detailUnsupported:"Ten widok wymaga zgodnego firmware i połączonego kanału sterowania.",detailEntity:"Wybierz urządzenie z dostępnymi danymi panelu.",detailReviewTitle:"Użyć pełnego widoku urządzenia?",detailReviewV2:"Szkic zostanie zaktualizowany do wersji 3 i otworzy pełny widok urządzenia. Nic nie zostanie jeszcze zapisane.",detailReviewV3:"Kafelek otworzy pełny widok urządzenia. Nic nie zostanie jeszcze zapisane.",detailConfirm:"Użyj widoku urządzenia",detailNotice:"Wybrano widok urządzenia. Zapisz układ, gdy będzie gotowy.",detailFacetUnavailable:"Część ustawień jest niedostępna. Panel pokazuje możliwości udostępnione przez Home Assistant.",
    panelUnsupported:"Ten widok wymaga zgodnego firmware i połączonego kanału sterowania.",panelEntity:"Wybierz dostępne urządzenie z obsługiwanymi elementami sterowania.",panelReviewTitle:"Użyć widoku urządzenia?",panelReviewV2:"Szkic zostanie zaktualizowany do wersji 3. Kafelek otworzy widok urządzenia. Nic nie zostanie jeszcze zapisane.",panelReviewV3:"Kafelek otworzy widok urządzenia. Nic nie zostanie jeszcze zapisane.",panelConfirm:"Użyj widoku urządzenia",panelNotice:"Wybrano widok urządzenia. Zapisz układ, gdy będzie gotowy.",timerPanelControl:"Otwórz minutnik",timerPanelHint:"Pokazuje pozostały czas, pauzę, wznawianie i ponowne uruchomienie. Samo otwarcie nie uruchamia minutnika.",remotePanelControl:"Otwórz pilot",remotePanelHint:"Pokazuje zasilanie i aktywności obsługiwane przez ten pilot. Samo otwarcie nie wysyła polecenia.",powerPanelControl:"Otwórz włącznik lub gniazdko",powerPanelHint:"Pokazuje bieżący stan i sterowanie zasilaniem. Samo otwarcie nie wysyła polecenia.",panelDuration:"Początkowy czas (sekundy, opcjonalnie)",panelDurationHint:"Wartość początkowa w widoku minutnika: od 1 do 86400 sekund. Puste pole oznacza jego bieżący czas. Edycja nie uruchamia minutnika.",
    humidityPanelControl:"Otwórz panel wilgotności",humidityPanelUnsupported:"Panel wilgotności wymaga zgodnego firmware i połączenia sterowania.",humidityPanelEntity:"Wybierz widoczny nawilżacz lub osuszacz z dostępnym sterowaniem.",humidityPanelHint:"Otwiera wilgotność docelową i zmierzoną, zasilanie i obsługiwane tryby. Samo otwarcie nie steruje urządzeniem.",humidityPanelReviewTitle:"Użyć panelu wilgotności?",humidityPanelReviewV2:"Szkic przejdzie na układ v3, a kafelek otworzy panel wilgotności. Niczego jeszcze nie zapisano.",humidityPanelReviewV3:"Kafelek będzie otwierać panel wilgotności. Niczego jeszcze nie zapisano.",humidityPanelConfirm:"Użyj panelu wilgotności",humidityPanelNotice:"Wybrano panel wilgotności. Zapisz układ, gdy będzie gotowy.",
    robotMowerHint:"Otwiera widok kosiarki z obsługiwanym koszeniem, pauzą i powrotem do bazy. Samo otwarcie nie wysyła polecenia.",robotAreaUnsupported:"Panel robota jest dostępny. To urządzenie nie udostępnia obsługiwanego wyboru pomieszczenia.",robotAreaUnmapped:"Panel robota jest dostępny. W Home Assistant nie przypisano do niego pomieszczeń.",robotAreaTooMany:"Panel robota jest dostępny. Wybór pomieszczenia obsługuje do ośmiu przypisanych pomieszczeń; to urządzenie ma ich więcej.",robotAreaLabels:"Panel robota jest dostępny. Sprawdź nazwy pomieszczeń: część jest za długa albo niejednoznaczna.",
    robotControl:"Otwórz panel robota lub kosiarki",robotUnsupported:"Panel urządzenia wymaga zgodnego firmware i połączenia sterowania.",robotEntity:"Wybierz dostępnego robota lub kosiarkę z obsługiwanym sterowaniem.",robotHint:"Otwiera dedykowany widok z dostępnymi operacjami, mocą ssania i przypisanymi pomieszczeniami. Samo otwarcie nie wysyła polecenia.",robotReviewTitle:"Użyć panelu urządzenia?",robotReviewV2:"Szkic przejdzie na układ v3, a kafelek otworzy panel urządzenia. Niczego jeszcze nie zapisano.",robotReviewV3:"Kafelek będzie otwierać panel urządzenia. Niczego jeszcze nie zapisano.",robotConfirm:"Użyj panelu urządzenia",robotNotice:"Wybrano panel urządzenia. Zapisz układ, gdy będzie gotowy.",
    fanControl:"Otwórz panel wentylatora",fanUnsupported:"Panel wentylatora wymaga zgodnego firmware i połączenia sterowania.",fanEntity:"Wybierz widoczny kafelek wentylatora z dostępnym sterowaniem.",fanHint:"Otwiera wspólny panel zasilania, prędkości, trybu, oscylacji i kierunku. Pokazuje obsługiwane funkcje. Samo otwarcie nie steruje urządzeniem.",fanReviewTitle:"Użyć panelu wentylatora?",fanReviewV2:"Szkic przejdzie na układ v3, a kafelek otworzy panel wentylatora. Niczego jeszcze nie zapisano.",fanReviewV3:"Kafelek będzie otwierać panel wentylatora. Niczego jeszcze nie zapisano.",fanConfirm:"Użyj panelu wentylatora",fanNotice:"Wybrano panel wentylatora. Zapisz układ, gdy będzie gotowy.",
    coverPanelControl:"Otwórz panel rolety lub bramy",coverPanelEntity:"Wybierz dostępne urządzenie z regulacją położenia, lameli lub sterowaniem ruchem.",coverPanelHint:"Otwiera osobne sekcje położenia i lameli. Każdy Stop dotyczy swojej sekcji. Pokazuje obsługiwane funkcje; samo otwarcie nie wysyła polecenia.",coverPanelReviewTitle:"Użyć panelu rolety lub bramy?",coverPanelReviewV2:"Szkic przejdzie na układ v3, a kafelek otworzy panel urządzenia. Niczego jeszcze nie zapisano.",coverPanelReviewV3:"Kafelek będzie otwierać panel urządzenia. Niczego jeszcze nie zapisano.",coverPanelConfirm:"Użyj panelu urządzenia",coverPanelNotice:"Wybrano panel urządzenia. Zapisz układ, gdy będzie gotowy.",
    coverControl:"Otwórz sterowanie roletą",coverUnsupported:"Sterowanie roletą wymaga zgodnego firmware i połączonego kanału sterowania.",coverEntity:"Wybierz widoczną kartę Encja dla dostępnej rolety z akcją Otwórz, Stop lub Zamknij.",coverHint:"Otwiera osobne przyciski Otwórz, Stop i Zamknij. Dostępne są tylko obsługiwane akcje. Podgląd nie wysyła poleceń.",coverReviewTitle:"Użyć sterowania roletą?",coverReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy sterowanie roletą. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",coverReviewV3:"Ta karta otworzy sterowanie roletą. Jeszcze nic nie zapisano.",coverConfirm:"Użyj sterowania roletą",coverNotice:"Sterowanie roletą wybrane w szkicu. Zapisz gotowy układ.",hiddenText:"Tekst ukryty",stateLabels:"Opisy stanów",stateLabelsHint:"Zastąp dokładne stany źródłowe krótkimi opisami na tej karcie informacyjnej. Pozostałe stany zachowają formatowanie Home Assistant. Nie można zmienić komunikatów braku danych i niedostępności.",stateLabelsKey:"Stan źródłowy",stateLabelsValue:"Tekst na ekranie",stateLabelsAdd:"Dodaj opis",stateLabelsRemove:"Usuń opis",stateLabelsApply:"Użyj opisów",stateLabelsInvalid:"Podaj różne stany i niepusty tekst bez znaków sterujących: do 32 bajtów UTF-8 w polu i ośmiu opisów. Stany unknown i unavailable są zastrzeżone.",stateLabelsChanged:"Kafelek lub szkic zmienił się. Otwórz jego opisy ponownie.",stateLabelsNotice:"Opisy stanów zmienione w szkicu. Zapisz gotowy układ.",
    tileEventPanel:"Panel zdarzenia",tileEventPanelCreate:"Dodaj panel zdarzenia",tileEventPanelReview:"Użyć panelu zdarzenia?",tileEventPanelHint:"Kafelek otwiera osobny widok. Dopiero przycisk Wyślij zdarzenie uruchamia zdarzenie Home Assistant. Podgląd i otwarcie niczego nie wysyłają.",tileEventPanelConfirm:"Użyj panelu zdarzenia",tileEventPanelUnavailable:"Wymagany jest połączony ekran z obsługą Action i panelu zdarzenia.",tileEventTitle:"Automatyzacja",tileEvent:"Przycisk automatyzacji",tileEventCreate:"Dodaj przycisk automatyzacji",tileEventHint:"Każde naciśnięcie jest dostępne jako zdarzenie w Home Assistant. Utwórz tam automatyzację, aby wybrać działanie. Podgląd niczego nie uruchamia.",tileEventReview:"Użyć przycisku automatyzacji?",tileEventReviewHint:"Przycisk zastąpi encję i dotychczasową akcję kafelka. Tytuł i wygląd zostaną zachowane. Zmiana nie jest jeszcze zapisana.",tileEventEmptyHint:"Utwórz przycisk, a następnie użyj jego zdarzenia w automatyzacji Home Assistant. Zmiana nie jest jeszcze zapisana.",tileEventConfirm:"Użyj przycisku automatyzacji",tileEventChanged:"Kafelek, ekran lub połączenie zmieniły się. Otwórz nowe potwierdzenie.",tileEventUnavailable:"Przyciski automatyzacji wymagają połączonego ekranu ze zgodną obsługą dotyku.",tileEventNotice:"Przycisk automatyzacji dodany do szkicu. Zapisz gotowy układ.",
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
    effectControl:"Wybierz efekt światła",effectUnsupported:"Wybór efektów wymaga połączonego urządzenia z obsługą tej funkcji.",effectEntity:"Wybierz dostępne światło z krótką listą różnych efektów oraz znanym efektem lub potwierdzonym brakiem aktywnego efektu.",effectHint:"Wybierz efekt, a następnie Zastosuj. Uruchomi to efekt i może włączyć światło.",effectReviewTitle:"Użyć wyboru efektów światła?",effectReviewV2:"Szkic przejdzie na układ v3, a karta otworzy wybór efektu. Zastosowanie efektu może włączyć światło. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",effectReviewV3:"Karta otworzy wybór efektu. Zastosowanie efektu może włączyć światło. Jeszcze nic nie zapisano.",effectConfirm:"Użyj wyboru efektów",effectNotice:"Dodano wybór efektów światła do szkicu. Zapisz, gdy będzie gotowy.",effectEmpty:"Brak efektu",
    humiModeControl:"Wybierz tryb pracy",humiModeUnsupported:"Wybór trybu wymaga zgodnego firmware i połączonego kanału wyboru.",humiModeEntity:"Wybierz dostępny nawilżacz lub osuszacz z obsługą trybów i krótką listą różnych opcji.",humiModeHint:"Wybierz tryb nawilżacza lub osuszacza na ekranie, a następnie Zastosuj.",humiModeReviewTitle:"Użyć wyboru trybu urządzenia?",humiModeReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór trybu urządzenia. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",humiModeReviewV3:"Ta karta otworzy wybór trybu urządzenia. Jeszcze nic nie zapisano.",humiModeConfirm:"Użyj wyboru trybu",humiModeNotice:"Dodano wybór trybu urządzenia do szkicu. Zapisz, gdy będzie gotowy.",humiModeNormal:"Normalny",humiModeEco:"Eco",humiModeAway:"Poza domem",humiModeBoost:"Przyspieszenie",humiModeComfort:"Komfort",humiModeHome:"W domu",humiModeSleep:"Sen",humiModeAuto:"Automatyczny",humiModeBaby:"Dla dziecka",
    humidifierPowerHint:"Dotknięcie kafelka na ekranie włącza lub wyłącza nawilżacz albo osuszacz.",humidifierPowerUnavailable:"Sterowanie jest niedostępne. Sprawdź połączenie i stan urządzenia.",humidifierOn:"Włączony",humidifierOff:"Wyłączony",
    horizontalControl:"Wybierz ruch poziomy",horizontalUnsupported:"Ruch poziomy wymaga zgodnego firmware i połączonego kanału wyboru.",horizontalEntity:"Wybierz dostępną klimatyzację z niezależnym ruchem poziomym i krótką listą różnych opcji.",horizontalHint:"Wybierz poziomy ruch żaluzji na ekranie, a następnie Zastosuj.",horizontalReviewTitle:"Użyć wyboru ruchu poziomego?",horizontalReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór ruchu poziomego. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",horizontalReviewV3:"Ta karta otworzy wybór ruchu poziomego. Jeszcze nic nie zapisano.",horizontalConfirm:"Użyj ruchu poziomego",horizontalNotice:"Dodano wybór ruchu poziomego do szkicu. Zapisz, gdy będzie gotowy.",horizontalOff:"Wyłączone",horizontalOn:"Włączone",
    swingControl:"Wybierz ruch żaluzji",swingUnsupported:"Ruch żaluzji wymaga zgodnego firmware i połączonego kanału wyboru.",swingEntity:"Wybierz dostępną klimatyzację z obsługą ruchu żaluzji i krótką listą różnych opcji.",swingHint:"Wybierz ruch żaluzji na ekranie, a następnie Zastosuj.",swingReviewTitle:"Użyć wyboru ruchu żaluzji?",swingReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór ruchu żaluzji. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",swingReviewV3:"Ta karta otworzy wybór ruchu żaluzji. Jeszcze nic nie zapisano.",swingConfirm:"Użyj wyboru żaluzji",swingNotice:"Dodano wybór ruchu żaluzji do szkicu. Zapisz, gdy będzie gotowy.",swingOff:"Wyłączone",swingOn:"Włączone",swingVertical:"Pionowo",swingHorizontal:"Poziomo",swingBoth:"Obie osie",
    airflowControl:"Wybierz tryb nawiewu",airflowUnsupported:"Tryb nawiewu wymaga zgodnego firmware i połączonego kanału wyboru.",airflowEntity:"Wybierz dostępną klimatyzację z obsługą trybów nawiewu i krótką listą różnych opcji.",airflowHint:"Wybierz tryb nawiewu na ekranie, a następnie Zastosuj.",airflowReviewTitle:"Użyć wyboru trybu nawiewu?",airflowReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór trybu nawiewu. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",airflowReviewV3:"Ta karta otworzy wybór trybu nawiewu. Jeszcze nic nie zapisano.",airflowConfirm:"Użyj wyboru nawiewu",airflowNotice:"Dodano wybór trybu nawiewu do szkicu. Zapisz, gdy będzie gotowy.",airflowAuto:"Automatyczny",airflowLow:"Niski",airflowMedium:"Średni",airflowHigh:"Wysoki",airflowOn:"Włączony",airflowOff:"Wyłączony",airflowTop:"Górny",airflowMiddle:"Środkowy",airflowFocus:"Skupiony",airflowDiffuse:"Rozproszony",
    presetControl:"Wybierz program klimatyzacji",presetUnsupported:"Programy klimatyzacji wymagają zgodnego firmware i połączonego kanału wyboru.",presetEntity:"Wybierz dostępny termostat z obsługą presetów i krótką listą różnych programów.",presetHint:"Wybierz program na ekranie, a następnie Zastosuj. Program może zmienić ustawienia urządzenia.",presetReviewTitle:"Użyć wyboru programu klimatyzacji?",presetReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór programu. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",presetReviewV3:"Ta karta otworzy wybór programu klimatyzacji. Jeszcze nic nie zapisano.",presetConfirm:"Użyj wyboru programu",presetNotice:"Dodano wybór programu do szkicu. Zapisz, gdy będzie gotowy.",presetNone:"Bez programu",presetEco:"Eco",presetComfort:"Komfort",presetSleep:"Sen",presetAway:"Poza domem",presetHome:"W domu",presetBoost:"Przyspieszenie",presetActivity:"Aktywność",
    hvacControl:"Wybierz tryb pracy",hvacUnsupported:"Wybór trybu wymaga zgodnego firmware i połączonego kanału wyboru.",hvacEntity:"Wybierz dostępny termostat ze znanym trybem i krótką listą różnych trybów pracy.",hvacHint:"Wybierz obsługiwany tryb na ekranie, a następnie Zastosuj. Temperatura docelowa ma osobną regulację.",hvacReviewTitle:"Użyć wyboru trybu pracy?",hvacReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór trybu pracy. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",hvacReviewV3:"Ta karta otworzy wybór trybu pracy. Jeszcze nic nie zapisano.",hvacConfirm:"Użyj wyboru trybu",hvacNotice:"Dodano wybór trybu pracy do szkicu. Zapisz, gdy będzie gotowy.",hvacOff:"Wyłączone",hvacHeat:"Ogrzewanie",hvacCool:"Chłodzenie",hvacHeatCool:"Grzanie/chłodzenie",hvacAuto:"Automatyczny",hvacDry:"Osuszanie",hvacFanOnly:"Wentylator",
    coverTiltControl:"Ustaw pochylenie lameli",coverTiltUnsupported:"Regulacja lameli wymaga połączonego urządzenia z obsługą tej funkcji.",coverTiltEntity:"Wybierz dostępną roletę z obsługą regulacji i znanym bieżącym pochyleniem lameli.",coverTiltHint:"Każde +/− zmienia pochylenie lameli o 1 punkt procentowy w zakresie HA 0–100%. Podnoszenie rolety i Stop lameli są osobnymi akcjami. Zamknięcie tego ekranu nie zatrzymuje ruchu.",coverTiltReviewTitle:"Użyć regulacji pochylenia lameli?",coverTiltReviewV2:"Szkic przejdzie na układ v3, a karta otworzy dokładną regulację lameli. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",coverTiltReviewV3:"Ta karta otworzy dokładną regulację lameli, niezależnie od procentu otwarcia rolety. Jeszcze nic nie zapisano.",coverTiltConfirm:"Użyj regulacji lameli",coverTiltNotice:"Dodano regulację lameli do szkicu. Zapisz, gdy będzie gotowy.",coverTiltValue:"Pochylenie",
    coverPositionControl:"Ustaw procent otwarcia",coverPositionUnsupported:"Regulacja otwarcia wymaga połączonego urządzenia z obsługą tej funkcji.",coverPositionEntity:"Wybierz dostępną roletę z obsługą ustawiania pozycji i znanym procentem otwarcia.",coverPositionHint:"Każde +/− zmienia otwarcie o 1 punkt procentowy: 0% zamknięte, 100% otwarte. Zamknięcie tego ekranu nie zatrzymuje ruchu; Stop jest osobną akcją rolety.",coverPositionReviewTitle:"Użyć regulacji procentu otwarcia?",coverPositionReviewV2:"Szkic przejdzie na układ v3, a karta otworzy dokładną regulację pozycji rolety. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",coverPositionReviewV3:"Ta karta otworzy dokładną regulację pozycji rolety. Otwieranie, zamykanie i Stop pozostają osobnymi akcjami. Jeszcze nic nie zapisano.",coverPositionConfirm:"Użyj regulacji otwarcia",coverPositionNotice:"Dodano regulację pozycji rolety do szkicu. Zapisz, gdy będzie gotowy.",coverOpening:"Otwarcie",
    vacuumPowerControl:"Wybierz moc odkurzacza",vacuumPowerUnsupported:"Wybór mocy odkurzacza wymaga połączonego urządzenia z obsługą tej funkcji.",vacuumPowerEntity:"Wybierz dostępny odkurzacz ze znaną mocą i krótką listą różnych obsługiwanych poziomów.",vacuumPowerHint:"Wybierz obsługiwaną moc ssania, a następnie Zastosuj. Rozpoczęcie sprzątania i powrót do bazy są osobnymi akcjami.",vacuumPowerReviewTitle:"Użyć wyboru mocy odkurzacza?",vacuumPowerReviewV2:"Szkic przejdzie na układ v3, a karta otworzy wybór mocy odkurzacza. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",vacuumPowerReviewV3:"Ta karta otworzy wybór mocy odkurzacza. Sprzątanie i powrót do bazy pozostają osobnymi akcjami. Jeszcze nic nie zapisano.",vacuumPowerConfirm:"Użyj wyboru mocy",vacuumPowerNotice:"Dodano wybór mocy odkurzacza do szkicu. Zapisz, gdy będzie gotowy.",vacuumQuiet:"Cicha",vacuumSilent:"Cicha",vacuumNormal:"Normalna",vacuumStandard:"Standardowa",vacuumTurbo:"Turbo",vacuumEco:"Eco",vacuumMax:"Maksymalna",vacuumStrong:"Silna",vacuumGentle:"Delikatna",vacuumOff:"Wyłączona",
    speedControl:"Wybierz bieg wentylatora",speedUnsupported:"Wybór biegów wymaga zgodnego firmware i połączonego kanału wyboru.",speedEntity:"Wybierz dostępny wentylator z 1–7 zadeklarowanymi biegami, zgodnym krokiem procentowym i znaną prędkością.",speedHint:"Wybierz obsługiwany bieg, a następnie Zastosuj. Zmiana prędkości może uruchomić lub zatrzymać wentylator, zależnie od integracji.",speedReviewTitle:"Użyć wyboru biegu wentylatora?",speedReviewV2:"Szkic przejdzie na układ v3, a karta otworzy wybór biegu. Zmiana prędkości może uruchomić lub zatrzymać wentylator. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",speedReviewV3:"Ta karta otworzy wybór biegu wentylatora. Zmiana prędkości może uruchomić lub zatrzymać wentylator. Jeszcze nic nie zapisano.",speedConfirm:"Użyj wyboru biegów",speedNotice:"Dodano wybór biegów do szkicu. Zapisz, gdy będzie gotowy.",
    kelvinControl:"Dostrój temperaturę barwową",kelvinUnsupported:"Temperatura barwowa wymaga zgodnego firmware i połączonego kanału liczbowego.",kelvinEntity:"Wybierz włączone światło w trybie temperatury barwowej, ze znaną całkowitą wartością kelwinów i dokładnym zakresem.",kelvinHint:"Precyzyjne dostrajanie co 1 K w aktywnym trybie temperatury barwowej. Zasilanie i inne tryby koloru są sterowane osobno.",kelvinReviewTitle:"Użyć precyzyjnej regulacji barwy?",kelvinReviewV2:"Szkic przejdzie na układ v3, a karta otworzy precyzyjną regulację co 1 K. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",kelvinReviewV3:"Ta karta otworzy regulację co 1 K, gdy światło jest włączone w trybie temperatury barwowej. Jeszcze nic nie zapisano.",kelvinConfirm:"Użyj precyzyjnej regulacji barwy",kelvinNotice:"Dodano regulację barwy do szkicu. Zapisz, gdy będzie gotowy.",
    climateHumidityControl:"Ustaw wilgotność klimatyzacji",climateHumidityUnsupported:"Wilgotność klimatyzacji wymaga zgodnego firmware i połączonego kanału liczbowego.",climateHumidityEntity:"Wybierz dostępną encję klimatyzacji z obsługą docelowej wilgotności, znaną nastawą i dokładnym całkowitym zakresem i krokiem.",climateHumidityHint:"Zmienia docelową wilgotność o obsługiwany krok. Tryb HVAC i docelowa temperatura mają osobne kontrolki.",climateHumidityReviewTitle:"Użyć regulacji wilgotności klimatyzacji?",climateHumidityReviewV2:"Szkic przejdzie na układ v3, a karta otworzy docelową wilgotność klimatyzacji. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",climateHumidityReviewV3:"Ta karta otworzy docelową wilgotność klimatyzacji. Tryb HVAC i temperatura pozostają osobno. Jeszcze nic nie zapisano.",climateHumidityConfirm:"Użyj wilgotności klimatyzacji",climateHumidityNotice:"Dodano wilgotność klimatyzacji do szkicu. Zapisz, gdy będzie gotowy.",
    humidityControl:"Ustaw wilgotność docelową",humidityUnsupported:"Regulacja wilgotności wymaga zgodnego firmware i połączonego kanału liczbowego.",humidityEntity:"Wybierz dostępny nawilżacz ze znaną nastawą oraz dokładnym całkowitym zakresem i krokiem.",humidityHint:"Zmienia docelową wilgotność o obsługiwany krok. Zasilanie i tryb pracy pozostają bez zmian.",humidityReviewTitle:"Użyć regulacji wilgotności docelowej?",humidityReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy regulację wilgotności. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",humidityReviewV3:"Ta karta otworzy regulację wilgotności docelowej. Jeszcze nic nie zapisano.",humidityConfirm:"Użyj regulacji wilgotności",humidityNotice:"Dodano regulację wilgotności do szkicu. Zapisz, gdy będzie gotowy.",
    thermostatReadOnly:"Otwiera podgląd termostatu. Integracja nie udostępnia potwierdzonej regulacji nastawy.",temperatureControl:"Otwórz termostat",temperatureTarget:"Cel",temperatureUnsupported:"Regulacja nastawy wymaga zgodnego firmware i połączonego kanału liczbowego.",temperatureEntity:"Wybierz dostępny termostat z jedną nastawą, dokładnym zakresem, krokiem i zgodną jednostką temperatury.",temperatureHint:"Zmienia jedną nastawę o obsługiwany krok. Tryb pracy pozostaje bez zmian. Nieznanej wartości nie można zmieniać.",temperatureReviewTitle:"Użyć regulacji temperatury docelowej?",temperatureReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy regulację temperatury. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",temperatureReviewV3:"Ta karta otworzy regulację temperatury docelowej. Jeszcze nic nie zapisano.",temperatureConfirm:"Użyj regulacji temperatury",temperatureNotice:"Dodano regulację temperatury do szkicu. Zapisz, gdy będzie gotowy.",
    directionControl:"Wybierz kierunek wentylatora",directionForward:"Do przodu",directionReverse:"Wstecz",directionUnsupported:"Wybór kierunku wymaga zgodnego firmware i połączonego kanału wyboru.",directionEntity:"Wybierz dostępny wentylator ze znanym kierunkiem i obsługą jego zmiany.",directionHint:"Wybierz Do przodu lub Wstecz na ekranie, a następnie Zastosuj. Zasilanie wentylatora pozostaje bez zmian.",directionReviewTitle:"Użyć wyboru kierunku wentylatora?",directionReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór kierunku. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",directionReviewV3:"Ta karta otworzy wybór kierunku wentylatora. Jeszcze nic nie zapisano.",directionConfirm:"Użyj wyboru kierunku",directionNotice:"Dodano wybór kierunku do szkicu. Zapisz, gdy będzie gotowy.",
    fanManual:"Tryb ręczny",fanOscillation:"Przełącz oscylację",fanOscillationOn:"Oscylacja wł.",fanOscillationOff:"Oscylacja wył.",fanOscillationHint:"Przełącza bieżący stan oscylacji. Zasilanie wentylatora pozostaje bez zmian. Podgląd nie wysyła polecenia.",
    calendarPlacement:"Wydarzenie kalendarza wymaga szerokiego wiersza informacyjnego na stronie Bezpieczeństwo.",calendarHint:"Pokazuje wydarzenie zgłaszane przez Home Assistant: datę, godzinę i krótki tytuł. To nie jest pełna agenda; dotknięcie nie wysyła polecenia.",
    personPlacement:"Nazwa strefy osoby wymaga szerokiego wiersza informacyjnego na stronie Bezpieczeństwo.",personHint:"Pokazuje obecność lub strefę zgłaszaną przez Home Assistant. Kolor podąża wyłącznie za stanem W domu. Dotknięcie nie wysyła polecenia; zdjęcia i mapa są osobnymi funkcjami.",
    vacuumRoom:"Sprzątaj pomieszczenie",vacuumRoomChoose:"Wybierz przypisane pomieszczenie",vacuumRoomUnavailable:"Wybrane pomieszczenie jest niedostępne",vacuumRoomHint:"Wybierz obszar już przypisany w ustawieniach odkurzacza w Home Assistant. Zmienia to tylko szkic. Aby rozpocząć, robot musi być w bazie, bezczynny lub wstrzymany.",vacuumRoomMissing:"Brak przypisanych pomieszczeń. Skonfiguruj mapowanie obszarów w ustawieniach encji odkurzacza w Home Assistant, a następnie odśwież.",vacuumRoomRefresh:"Odśwież pomieszczenia",
    vacuumStart:"Rozpocznij / wznów sprzątanie",vacuumPause:"Wstrzymaj sprzątanie",vacuumStop:"Zatrzymaj sprzątanie",vacuumDock:"Wróć do bazy",vacuumLocate:"Znajdź robota",vacuumSpot:"Posprzątaj bieżące miejsce",vacuumActionsHint:"Wybierz działanie po dotknięciu karty. Te przyciski tylko edytują układ. Karta pokazuje zgłoszoną aktywność; polecenie nie zastępuje potwierdzenia stanu. Moc ssania ustawia się osobno.",
    mediaStop:"Zatrzymaj odtwarzanie",mediaStatePrefix:"Stan: ",mediaStopHint:"Ustaw kafelek do zatrzymywania wybranego odtwarzacza. Będzie aktywny podczas odtwarzania, buforowania lub pauzy.",
    mediaVolumeTarget:"Ustaw głośność",mediaVolumePercent:"Docelowa głośność (%)",mediaVolumeTargetHint:"Ustaw poziom, o który poprosi kafelek: od 0 do 100%. Kafelek pokazuje zgłoszoną głośność. Edycja szkicu nie steruje odtwarzaczem. To stały poziom docelowy; nie dodaje suwaka na ekranie urządzenia.",
    mediaLouder:"Głośniej",mediaQuieter:"Ciszej",mediaVolumeHint:"Wybierz Głośniej lub Ciszej dla kafelka. Każde dotknięcie zmienia głośność o krok odtwarzacza. Podgląd pokazuje zgłoszoną głośność; te przyciski zmieniają tylko szkic.",
    mediaShuffle:"Losowo",mediaUnshuffle:"Po kolei",mediaShuffleField:"Odtwarzaj losowo",mediaShuffleService:"Odtwarzanie losowe",mediaShuffled:"Losowo",mediaInOrder:"Po kolei",mediaShuffleHint:"Wybierz działanie kafelka. Te przyciski zmieniają tylko szkic. Losowanie wynika ze stanu odtwarzacza i zachowuje odtwarzanie, głośność oraz powtarzanie.",
    mediaRepeatControl:"Wybierz tryb powtarzania",mediaRepeatUnsupported:"Powtarzanie wymaga zgodnego, połączonego kanału opcji.",mediaRepeatEntity:"Wybierz odtwarzacz obsługujący powtarzanie ze znanym bieżącym trybem.",mediaRepeatHint:"Wybierz tryb powtarzania na ekranie, a następnie Zastosuj. Odtwarzanie, utwór i głośność pozostaną zachowane.",mediaRepeatReviewTitle:"Użyć wyboru powtarzania?",mediaRepeatReviewV2:"Szkic przejdzie na układ v3 i otworzy wybór powtarzania. Inne karty pozostaną zachowane. Jeszcze nic nie zapisano.",mediaRepeatReviewV3:"Karta otworzy wybór powtarzania. Jeszcze nic nie zapisano.",mediaRepeatConfirm:"Użyj wyboru powtarzania",mediaRepeatNotice:"Dodano wybór powtarzania do szkicu. Zapisz, gdy będzie gotowy.",mediaRepeatPrefix:"Powt.: ",repeatOff:"Wyłączone",repeatOne:"Jeden utwór",repeatAll:"Cała kolejka",
    mediaSoundPrefix:"Tryb: ",mediaSoundControl:"Wybierz tryb dźwięku",mediaSoundUnsupported:"Tryby dźwięku wymagają zgodnego, połączonego kanału opcji.",mediaSoundEntity:"Wybierz dostępnego odtwarzacza ze znanym trybem i krótką listą różnych trybów dźwięku.",mediaSoundHint:"Wybierz tryb dźwięku na ekranie, a następnie Zastosuj. Zmienia przetwarzanie dźwięku w wybranym odtwarzaczu; nie wysyła poleceń odtwarzania, zasilania ani głośności.",mediaSoundReviewTitle:"Użyć wyboru trybu dźwięku?",mediaSoundReviewV2:"Szkic przejdzie na układ v3 i otworzy wybór trybu dźwięku. Inne karty pozostaną zachowane. Jeszcze nic nie zapisano.",mediaSoundReviewV3:"Karta otworzy wybór trybu dźwięku. Jeszcze nic nie zapisano.",mediaSoundConfirm:"Użyj wyboru trybu dźwięku",mediaSoundNotice:"Dodano wybór trybu dźwięku do szkicu. Zapisz, gdy będzie gotowy.",
    mediaSourceControl:"Wybierz źródło odtwarzacza",mediaSourceUnsupported:"Wybór źródła wymaga zgodnego, połączonego kanału opcji.",mediaSourceEntity:"Wybierz dostępnego odtwarzacza ze znanym źródłem i krótką listą różnych wejść.",mediaSourceHint:"Wybierz źródło na ekranie, a następnie Zastosuj. Nie wysyła to poleceń odtwarzania, zasilania ani głośności.",mediaSourceReviewTitle:"Użyć wyboru źródła?",mediaSourceReviewV2:"Szkic przejdzie na układ v3 i otworzy wybór źródła. Inne karty pozostaną zachowane. Jeszcze nic nie zapisano.",mediaSourceReviewV3:"Karta otworzy wybór źródła. Jeszcze nic nie zapisano.",mediaSourceConfirm:"Użyj wyboru źródła",mediaSourceNotice:"Dodano wybór źródła do szkicu. Zapisz, gdy będzie gotowy.",
    activityControl:"Wybierz aktywność pilota",activityUnsupported:"Wybór aktywności wymaga zgodnego, połączonego kanału opcji.",activityEntity:"Wybierz dostępnego pilota z obsługą aktywności i krótką listą różnych nazw.",activityHint:"Wybierz aktywność na ekranie, a następnie Zastosuj. Home nadal pokazuje stan zasilania.",activityReviewTitle:"Użyć wyboru aktywności?",activityReviewV2:"Szkic przejdzie na układ v3 i otworzy wybór aktywności. Inne karty pozostaną zachowane. Jeszcze nic nie zapisano.",activityReviewV3:"Karta otworzy wybór aktywności. Jeszcze nic nie zapisano.",activityConfirm:"Użyj wyboru aktywności",activityNotice:"Dodano wybór aktywności do szkicu. Zapisz, gdy będzie gotowy.",
    mediaMute:"Wycisz",mediaUnmute:"Przywróć dźwięk",mediaMuteField:"Wycisz dźwięk",mediaMuteService:"Wyciszenie odtwarzacza",mediaMuted:"Wyciszony",mediaSoundOn:"Dźwięk wł.",mediaOff:"Wyłączony",mediaMuteHint:"Wybierz działanie po dotknięciu kafelka. Te przyciski zmieniają tylko szkic. Wyciszenie wynika ze stanu odtwarzacza; nie zmienia odtwarzania, utworu ani głośności.",
    remoteOn:"Włącz pilota",remoteOff:"Wyłącz pilota",remoteHint:"Wybierz jawne polecenie zasilania dla kafelka. Te przyciski zmieniają tylko szkic. Karta pokazuje stan zgłoszony przez Home Assistant; wykonane już przejście jest nieaktywne. Aktywności i nauczone komendy konfiguruje się osobno.",
    mowerStart:"Rozpocznij / wznów koszenie",mowerPause:"Wstrzymaj koszenie",mowerDock:"Wróć do bazy",mowerHint:"Wybierz działanie po dotknięciu karty. Te przyciski tylko edytują układ. Start wznawia również wstrzymane koszenie. Karta jest nieaktywna, gdy bieżący stan lub możliwości nie pozwalają wykonać wybranego polecenia.",
    textPanelControl:"Otwórz edytor tekstu",textPanelUnsupported:"Ten widok wymaga połączonego urządzenia z profilem tekstowym.",textPanelEntity:"Dane widoku tekstu są niedostępne lub nieobsługiwane.",textPanelHint:"Zmień lokalny szkic i wybierz Zapisz, aby przesłać pełną wartość do Home Assistant.",textPanelPassive:"Ten pomocnik udostępnia teraz tylko podgląd.",textPanelReview:"Użyj kafelka encji otwierającego edytor tekstu. Formatowanie kafelka czujnika zostanie usunięte. Zmieniasz tylko szkic układu, który trzeba osobno zapisać. Żaden tekst nie zostanie wysłany.",textPanelHidden:"Tekst ukryty",textPanelPattern:"Edycja tekstu ze wzorcem nie jest obsługiwana.",textPanelBounds:"Nieobsługiwane ograniczenia długości tekstu.",textPanelLength:"Obecny tekst nie mieści się w obsługiwanym zakresie długości.",textPanelCharacters:"Obecny tekst zawiera nieobsługiwane znaki.",textPanelEmpty:"Pusty tekst",
    datetimePanelControl:"Otwórz edytor daty i czasu",datetimePanelUnsupported:"Ten widok wymaga połączonego urządzenia z profilem daty i czasu.",datetimePanelEntity:"Dane widoku daty i czasu są niedostępne lub nieobsługiwane.",datetimePanelHint:"Zmień lokalny szkic na urządzeniu i wybierz Zapisz, aby przesłać jedną pełną wartość do Home Assistant.",datetimePanelPassive:"Pomocnik udostępnia teraz tylko podgląd; usługa ustawiania daty i czasu jest niedostępna.",datetimePanelReview:"Użyj kafelka encji otwierającego edytor daty i czasu. Formatowanie dostępne tylko dla kafelka czujnika zostanie usunięte. To zmiana szkicu do układu v3; żadna wartość nie zostanie wysłana i nic nie jest jeszcze zapisane.",datetimePanelWallHint:"Pomocnik przechowuje datę kalendarzową i/lub lokalną godzinę. Nie wybiera chwili w UTC ani wystąpienia powtarzającej się godziny.",
    datetimePlacement:"Data i godzina wymagają szerokiego kafelka tekstowego.",
    entity:"Encja",changeEntity:"Wybierz encję z biblioteki",title:"Tytuł",icon:"Ikona",palette:"Kolor",visible:"Pokaż na ekranie",
    type:"Typ karty",entityType:"Encja",sensorType:"Informacja",actionType:"Akcja",tap:"Po dotknięciu",default:"Akcja domyślna",none:"Bez działania",
    service:"Wybrana akcja",chooseService:"Wybierz akcję",noActions:"Ta encja nie ma obecnie obsługiwanych akcji.",
    actionUnavailable:"Zapisana akcja jest obecnie niedostępna. Przed zapisem wybierz obsługiwaną akcję.",
    controlProfileChanged:"Profil ekranu zmienił się. Wczytaj zapisany układ przed wybraniem sterowania światłem.",
    numberControl:"Otwórz sterowanie liczbą",numberUnsupported:"Sterowanie liczbą wymaga zgodnego firmware i uzgodnionego kanału sterowania encjami.",numberEntity:"Wybierz widoczną kartę Encja dla dostępnej encji Number lub pomocnika z obsługiwaną dziedziną liczbową.",numberHint:"Otwiera przyciski minus/plus. Podgląd nie wysyła poleceń; Home Assistant ponownie sprawdza wartość i parametry kroku.",numberReviewTitle:"Użyć sterowania liczbą?",numberReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy sterowanie liczbą. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",numberReviewV3:"Ta karta otworzy sterowanie liczbą. Jeszcze nic nie zapisano.",numberConfirm:"Użyj sterowania liczbą",numberNotice:"Wybrano sterowanie liczbą w szkicu. Zapisz układ, gdy będzie gotowy.",
    control:"Otwórz sterowanie światłem",controlHint:"Otwiera sterowanie światłem na urządzeniu. Podgląd nie wysyła poleceń; Home Assistant ponownie sprawdza Włącz/Wyłącz i jasność.",controlUnsupported:"Sterowanie światłem wymaga zgodnego firmware oraz połączonego, uzgodnionego kanału sterowania. Dotychczasowe akcje dotknięcia pozostają bez zmian.",controlEntity:"Wybierz widoczną kartę Encja dla dostępnego światła z obsługiwaną akcją zasilania.",controlBrightness:"Jasność jest dostępna, gdy światło ją obsługuje. Nieznana wartość ma oznaczenie --, bez wymyślonego procentu.",controlPowerOnly:"Jasność niedostępna. Dostępne będą tylko obsługiwane akcje Włącz/Wyłącz.",controlReviewTitle:"Użyć sterowania światłem?",controlReviewV2:"Szkic przejdzie na układ v3, a ta karta będzie otwierać sterowanie światłem. Pozostałe identyfikatory, miejsca i akcje kart zostaną zachowane. Starszy firmware pozostawi tę kartę bez działania. Jeszcze nic nie zapisano.",controlReviewV3:"Ta karta będzie otwierać sterowanie światłem. Jeszcze nic nie zapisano; sprawdź szkic i zapisz go, gdy będzie gotowy.",controlConfirm:"Użyj sterowania światłem",controlChanged:"Ekran, szkic lub możliwości światła zmieniły się. Sprawdź bieżącą kartę i spróbuj ponownie.",controlNotice:"Wybrano sterowanie światłem w szkicu. Zapisz układ, gdy będzie gotowy.",
    parameters:"Ustawienia akcji",optional:"Opcjonalne",required:"Wymagane",true:"Tak",false:"Nie",rgb:"Czerwony, zielony, niebieski (0–255)",
    timerDuration:"Czas (sekundy)",timerDurationHint:"Wpisz 1–86400 sekund dla stałego czasu. Zostaw puste, aby przy wznawianiu zachować pozostały czas timera.",
    stateColor:"Wyróżniaj stan aktywny",stateColorHint:"Wybrana paleta oznacza włączenie, otwarcie lub wykrycie. Wyłączenie i brak danych mają spokojniejsze tło.",
    precision:"Miejsca po przecinku",precisionAuto:"Z Home Assistant",precisionHint:"Zmiana dotyczy tylko tej karty liczbowej. Daty, opisy i czas trwania zachowują dotychczasowy format.",outOfRange:"Poza zakresem",
    autoIcon:"Według typu czujnika",
    presencePresent:"Obecność",presenceAway:"Brak obecności",
    automationEnable:"Włącz",automationDisable:"Wyłącz",automationRun:"Uruchom",
    automationHint:"Domyślne dotknięcie włącza lub wyłącza przyszłe wyzwolenia. Trwające wykonanie kończy się normalnie. Wybierz osobno Uruchom, aby wykonać akcje.",
    automationRunHint:"Uruchom wykonuje automatyzację jeden raz. Pomiń warunki: Tak lub puste ignoruje jej warunki; Nie je sprawdza.",
    automationOffHint:"Zatrzymaj trwające akcje: Tak lub puste zatrzymuje bieżące wykonanie; Nie pozwala mu się zakończyć.",
    skipConditions:"Pomiń warunki",stopActions:"Zatrzymaj trwające akcje",
    choiceControl:"Otwórz wybór opcji",choiceUnsupported:"Wybór opcji wymaga zgodnego firmware i połączonego kanału sterowania.",choiceEntity:"Wybierz widoczną kartę Encja dla dostępnej encji Select lub presetu wentylatora z jedną do ośmiu krótkich, różnych opcji.",choiceHint:"Wybierz opcję na ekranie, a następnie Zastosuj. Wybór w podglądzie nie wysyła polecenia.",choiceReviewTitle:"Użyć wyboru opcji?",choiceReviewV2:"Szkic przejdzie na układ v3, a ta karta otworzy wybór opcji. Pozostałe karty zostaną zachowane. Jeszcze nic nie zapisano.",choiceReviewV3:"Ta karta otworzy wybór opcji. Jeszcze nic nie zapisano.",choiceConfirm:"Użyj wyboru opcji",choiceNotice:"Dodano wybór opcji do szkicu. Zapisz, gdy będzie gotowy.",
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
const AEH_ICONS = {camera:"mdi:video-outline",vacuum:"mdi:robot-vacuum",mower:"mdi:robot-mower",action:"mdi:gesture-tap-button",alarm:"mdi:shield-home-outline",climate:"mdi:thermostat",cover:"mdi:blinds-horizontal",fan:"mdi:fan",light:"mdi:lightbulb-outline",lock:"mdi:lock-outline",scene:"mdi:palette-outline",speed:"mdi:speedometer",switch:"mdi:power",sensor:"mdi:thermometer",humidity:"mdi:water",door:"mdi:window-closed-variant",presence:"mdi:account-group-outline",clock:"mdi:alarm",webhook:"mdi:webhook"};
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
const AEH_COMPARE = value => JSON.stringify({version:value?.version,profile:value?.profile,home_order:value?.home_order,cards:[...(value?.cards || [])].sort((a,b) => a.slot-b.slot)});
const AEH_ESCAPE = value => String(value ?? "").replaceAll("&","&amp;").replaceAll('"',"&quot;").replaceAll("<","&lt;").replaceAll(">","&gt;");
// Duration arithmetic stays exact and bounded; these are seconds multipliers
// and decimal denominators, not a browser timer or a device rendering loop.
const AEH_DURATION_UNITS = {"μs":[1n,6],ms:[1n,3],s:[1n,0],min:[60n,0],h:[3600n,0],d:[86400n,0],w:[604800n,0]};
const AEH_DRAFT_FIELDS = new Set(["volume_level","cleaning_area_id","brightness_pct","color_temp_kelvin","rgb_color","percentage","oscillating","direction","preset_mode","position","tilt_position","temperature","target_temp_low","target_temp_high","humidity","hvac_mode","fan_mode","fan_speed","swing_mode","swing_horizontal_mode","mode","effect","value","option"]);
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
    this._entityStateRefs = new WeakMap(); this._cataloguePending = null; this._selectedEntityPending = null;
    this._entityMetadataRequests = new Map(); this._entityMetadataReads = new Map(); this._entityMetadataOrder = 0;
    this._precisionFormats = new Map();
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
    const controlsBefore = this.controlAvailability(this.cardAt(this._selectedSlot),this.cardControlKind(this.cardAt(this._selectedSlot))).ready, eventsBefore = `${this.eventAvailability()}:${this.tileEventPanelAvailability()}:${this.cameraPreviewStatusKey()}:${this.actionParametersAvailability().ready}`;
    if ((this._hass?.user?.id ?? null) !== (value?.user?.id ?? null)) { this.resetClipboardIntent(); this.resetCardSelection(); }
    if (this._hass?.user?.id && this._hass.user.id !== value?.user?.id) {
      this.persistDraft(); this._selectionEpoch++; this._loadRequest++;
      this._data = null; this._draft = null; this._saved = null; this._entryId = "";
      this._loading = false; this._busy = false; this._pending = null; this._entityIndex.clear();
      this._entityStateRefs = new WeakMap(); this._cataloguePending = null; this._selectedEntityPending = null;
      this._entityMetadataRequests = new Map(); this._entityMetadataReads = new Map(); this._entityMetadataOrder = 0;
      window.clearTimeout(this._draftTimer); this.cancelMove(false);
    }
    this._hass = value;
    if (this.isConnected && !this._data && !this._loading) this.load();
    else if (this._data) {
      this.paintValues();
      if (controlsBefore !== this.controlAvailability(this.cardAt(this._selectedSlot),this.cardControlKind(this.cardAt(this._selectedSlot))).ready || eventsBefore !== `${this.eventAvailability()}:${this.tileEventPanelAvailability()}:${this.cameraPreviewStatusKey()}:${this.actionParametersAvailability().ready}`) this.paintControlAvailability();
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
    this._entityStateRefs = new WeakMap(); this._cataloguePending = null; this._selectedEntityPending = null;
    this._entityMetadataRequests = new Map(); this._entityMetadataReads = new Map(); this._entityMetadataOrder = 0;
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
    if (!keys(layout,["version","profile","cards",...(layout && Object.hasOwn(layout,"home_order") ? ["home_order"] : [])]) || ![2,3].includes(layout.version) || (layout.version === 3 && (!Array.isArray(this.profile.layout_versions) || !this.profile.layout_versions.includes(3))) || layout.profile !== this.profile.id || !Array.isArray(layout.cards) || layout.cards.length > this.profile.max_cards) fail();
    if (Object.hasOwn(layout,"home_order") && (!Array.isArray(this.profile.carousel_order) || !Array.isArray(layout.home_order) ||
        layout.home_order[0] !== "home-1" || !layout.home_order.includes("home-3") ||
        new Set(layout.home_order).size !== layout.home_order.length ||
        layout.home_order.some(id => !this.profile.carousel_order.includes(id)))) fail();
    const ids = new Set(), slots = new Set();
    for (const card of layout.cards) {
      if (!keys(card,["id","slot","type","entity_id","title","icon","palette","visible","action","state_color","display_precision","state_labels"]) || typeof card.id !== "string" || !/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(card.id) || !Number.isInteger(card.slot) || ids.has(card.id) || slots.has(card.slot)) fail();
      if (Object.hasOwn(card,"state_labels") && (this.profile.schema_state_labels !== true || !this.stateLabelsEligible(card) || !object(card.state_labels) || this.labelsFromRows(Object.entries(card.state_labels).map(([key,label])=>({key,label}))) === null)) fail();
      if (Object.hasOwn(card,"state_color") && (typeof card.state_color !== "boolean" || (card.state_color && !this.stateColorEligible(card)))) fail();
      if (Object.hasOwn(card,"display_precision") && (!this.precisionEligible(card) || !Number.isInteger(card.display_precision) || card.display_precision < 0 || card.display_precision > 6)) fail();
      if (card.icon === "auto" && !this.autoIconEligible(card)) fail();
      const slot = this.profile.slots.find(item => item.slot === card.slot);
      if (this.isRestrictedTextCard(card) && !this.acceptsCard(slot,card)) throw new Error(this.textPlacementMessage(card));
      if (!slot || !this.acceptsCard(slot,card) || typeof card.visible !== "boolean" || (!slot.editable && card.visible) || typeof card.entity_id !== "string" || card.entity_id.length > 128 || (card.entity_id && !/^[a-z_][a-z0-9_]*\.[a-z0-9_]+$/.test(card.entity_id)) || typeof card.title !== "string" || [...card.title].length > 40 || !this._data.icons.includes(card.icon) || !this._data.palettes.includes(card.palette)) fail();
      ids.add(card.id); slots.add(card.slot);
      const action = card.action;
      if (!keys(action,["kind","service","data","control","property","initial_duration","detail","skip_condition","stop_actions","duration_seconds","parameters"]) || !["none","default","service","control","event","fan_oscillation","camera_preview"].includes(action.kind) || (card.type === "sensor" && action.kind !== "none" && !this.validExtraPanelAction(card)) || Object.hasOwn(action,"initial_duration") && action.control!=="panel") fail();
      if (action.kind==="camera_preview") {
        if (layout.version!==3 || !this.validCameraPreview(card) || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (Object.hasOwn(action,"duration_seconds") || card.entity_id.startsWith("camera.") && action.kind!=="none") fail();
      if (Object.hasOwn(action,"parameters") && !this.isActionParametersAction(card)) fail();
      if ((Object.hasOwn(action,"skip_condition") || Object.hasOwn(action,"stop_actions")) && !this.isActionPanelAction(card)) fail();
      if (action.control==="panel" && action.property==="tile_event") {
        if(layout.version!==3 || !this.validTileEventPanel(card) || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (action.control==="panel" && action.property==="action") {
        if (layout.version!==3 || !(this.validActionPanelAction(card) || this.validActionParametersAction(card)) || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (Object.hasOwn(action,"detail") || action.control==="panel" && action.property==="climate") {
        if (layout.version!==3 || !this.validDetailAction(card) || card.type!=="entity" || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (action.control === "panel" && action.property==="text") {
        if(layout.version!==3 || !this.validTextPanelAction(card) || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (action.control === "panel" && action.property==="datetime") {
        if (layout.version!==3 || !this.validDatetimePanelAction(card) || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (action.control === "panel" && action.property==="media") {
        if (layout.version!==3 || !this.validMediaPanelAction(card) || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (action.control === "panel" && ["info","lock","agenda","statistics"].includes(action.property)) {
        if (layout.version!==3 || !this.validExtraPanelAction(card) || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (action.control === "panel") {
        if (layout.version !== 3 || !this.validPanelAction(card) || card.type !== "entity" || !slot.editable || slot.hidden || card.slot < 2) fail();
        continue;
      }
      if (Object.hasOwn(action,"property")) {
        const direction=this.profile.schema_fan_direction===true && action.control==="choice" && action.property==="direction" && card.entity_id.startsWith("fan.");
        const effect=this.profile.schema_light_effect===true && action.control==="choice" && action.property==="effect" && card.entity_id.startsWith("light.");
        const covertilt=this.profile.schema_cover_tilt===true && action.control==="number" && action.property==="tilt_position" && card.entity_id.startsWith("cover.");
        const coverposition=this.profile.schema_cover_position===true && action.control==="number" && action.property==="position" && card.entity_id.startsWith("cover.");
        const mediarepeat=this.profile.schema_media_repeat===true && action.control==="choice" && action.property==="repeat" && card.entity_id.startsWith("media_player.");
        const mediasound=this.profile.schema_media_sound_mode===true && action.control==="choice" && action.property==="sound_mode" && card.entity_id.startsWith("media_player.");
        const mediasource=this.profile.schema_media_source===true && action.control==="choice" && action.property==="source" && card.entity_id.startsWith("media_player.");
        const remoteactivity=this.profile.schema_remote_activity===true && action.control==="choice" && action.property==="activity" && card.entity_id.startsWith("remote.");
        const vacuumfan=this.profile.schema_vacuum_fan_speed===true && action.control==="choice" && action.property==="fan_speed" && card.entity_id.startsWith("vacuum.");
        const speed=this.profile.schema_fan_speed===true && action.control==="choice" && action.property==="percentage" && card.entity_id.startsWith("fan.");
        const kelvin=this.profile.schema_light_color_temperature===true && action.control==="number" && action.property==="color_temp_kelvin" && card.entity_id.startsWith("light.");
        const humidity=action.control==="number" && action.property==="humidity" && (this.profile.schema_humidifier_humidity===true && card.entity_id.startsWith("humidifier.") || this.profile.schema_climate_humidity===true && card.entity_id.startsWith("climate."));
        const temperature=this.profile.schema_climate_temperature===true && action.control==="number" && action.property==="temperature" && card.entity_id.startsWith("climate.");
        const hvac=this.profile.schema_climate_hvac_mode===true && action.control==="choice" && action.property==="hvac_mode" && card.entity_id.startsWith("climate.");
        const preset=this.profile.schema_climate_preset_mode===true && action.control==="choice" && action.property==="preset_mode" && card.entity_id.startsWith("climate.");
        const airflow=this.profile.schema_climate_fan_mode===true && action.control==="choice" && action.property==="fan_mode" && card.entity_id.startsWith("climate.");
        const swing=this.profile.schema_climate_swing_mode===true && action.control==="choice" && action.property==="swing_mode" && card.entity_id.startsWith("climate.");
        const horizontal=this.profile.schema_climate_swing_horizontal_mode===true && action.control==="choice" && action.property==="swing_horizontal_mode" && card.entity_id.startsWith("climate.");
        const humidifier=this.profile.schema_humidifier_mode===true && action.control==="choice" && action.property==="mode" && card.entity_id.startsWith("humidifier.");
        if (layout.version!==3 || action.kind!=="control" || Object.keys(action).length!==3 || !(mediasound || mediarepeat || mediasource || remoteactivity || covertilt || coverposition || vacuumfan || speed || kelvin || effect || direction || humidity || temperature || hvac || preset || airflow || swing || horizontal || humidifier) || card.type!=="entity" || !slot.editable || slot.hidden || card.slot<2) fail();
        continue;
      }
      if (action.kind === "fan_oscillation") {
        if (layout.version !== 3 || this.profile.schema_fan_oscillation !== true || Object.keys(action).length !== 1 || !card.entity_id.startsWith("fan.")) fail();
        continue;
      }
      if (action.kind === "event") {
        if (layout.version !== 3 || this.profile.schema_event_actions !== true || Object.keys(action).length !== 1 || card.type !== "action" || card.entity_id !== "" || !slot.editable || slot.hidden || card.slot < 2) fail();
        continue;
      }
      if (action.kind === "control") {
        if (layout.version !== 3 || Object.keys(action).length !== 2 || !((action.control === "light" && card.entity_id.startsWith("light.")) || (action.control === "number" && this.isNumberEntity(card)) || (action.control === "choice" && this.isChoiceEntity(card)) || (action.control === "cover" && card.entity_id.startsWith("cover.")) || (action.control === "fan" && this.profile.schema_control_types?.includes("fan") && card.entity_id.startsWith("fan.")) || (action.control === "humidifier" && this.profile.schema_control_types?.includes("humidifier") && card.entity_id.startsWith("humidifier.")) || (action.control === "robot" && this.profile.schema_control_types?.includes("robot") && ["vacuum","lawn_mower"].includes(card.entity_id.split(".")[0]))) || card.type !== "entity" || !slot.editable || slot.hidden || card.slot < 2) fail();
        continue;
      }
      if (Object.hasOwn(action,"control")) fail();
      if (action.kind !== "service") { if (Object.keys(action).length !== 1) fail(); continue; }
      if (typeof action.service !== "string" || !/^[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*$/.test(action.service) || !object(action.data)) fail();
      if (Object.hasOwn(action.data,"cleaning_area_id") && (this.profile.schema_vacuum_area!==true || action.service!=="vacuum.clean_area" || !card.entity_id.startsWith("vacuum.") || typeof action.data.cleaning_area_id!=="string")) fail();
      if (Object.hasOwn(action.data,"fan_speed") && action.service!=="vacuum.set_fan_speed") fail();
      if (Object.hasOwn(action.data,"volume_level") && (this.profile.schema_media_volume_target!==true || action.service!=="media_player.volume_set" || !card.entity_id.startsWith("media_player.") || typeof action.data.volume_level!=="number" || !Number.isFinite(action.data.volume_level) || action.data.volume_level<0 || action.data.volume_level>1)) fail();
      if (Object.hasOwn(action.data,"effect") && action.service!=="light.turn_on") fail();
      if (card.entity_id.startsWith("humidifier.") && ["humidifier.turn_on","humidifier.turn_off","humidifier.toggle"].includes(action.service) && Object.keys(action.data).length) fail();
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
    const controlsBefore = this.controlAvailability(this.cardAt(this._selectedSlot),this.cardControlKind(this.cardAt(this._selectedSlot))).ready, eventsBefore = `${this.eventAvailability()}:${this.tileEventPanelAvailability()}:${this.cameraPreviewStatusKey()}:${this.actionParametersAvailability().ready}`;
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
      if (controlsBefore !== this.controlAvailability(this.cardAt(this._selectedSlot),this.cardControlKind(this.cardAt(this._selectedSlot))).ready || eventsBefore !== `${this.eventAvailability()}:${this.tileEventPanelAvailability()}:${this.cameraPreviewStatusKey()}:${this.actionParametersAvailability().ready}`) this.paintControlAvailability();
      this.refreshEntityMetadata();
    } catch (_error) {
      if (id !== this._entryId || epoch !== this._selectionEpoch || revision !== this._saved?.revision || request !== this._statusRequest || this._busy || !this.isConnected) return;
      this._statusError = true; this.paintStatus();
      if (controlsBefore !== this.controlAvailability(this.cardAt(this._selectedSlot),this.cardControlKind(this.cardAt(this._selectedSlot))).ready || eventsBefore !== `${this.eventAvailability()}:${this.tileEventPanelAvailability()}:${this.cameraPreviewStatusKey()}:${this.actionParametersAvailability().ready}`) this.paintControlAvailability();
    }
  }
  async fetchCatalogue() {
    if (!this._entryId) return;
    const request = ++this._catalogueRequest, id = this._entryId, epoch = this._selectionEpoch, order = ++this._entityMetadataOrder;
    const states = this._hass?.states;
    this._cataloguePending = request;
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
      this._catalogue = entities.map(entity => this.cacheEntityMetadata(entity,states,order) || entity);
      this._catalogueTotal = result.total; this._truncated = result.truncated;
      this._catalogueError = ""; this.paintLibrary(); this.paintValues();
      if (!this.shadowRoot.querySelector(".inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
    } catch (error) {
      if (id !== this._entryId || epoch !== this._selectionEpoch || request !== this._catalogueRequest) return;
      this._catalogueError = this.errorText(error); this.paintLibrary();
    } finally {
      if (this._cataloguePending === request) this._cataloguePending = null;
    }
  }
  entityMetadataStale(entity) {
    return !!this._hass?.states && !!entity && this._entityStateRefs.has(entity) &&
      this._entityStateRefs.get(entity) !== this._hass.states[entity.entity_id];
  }
  refreshEntityMetadata() {
    // Use the existing status cadence. State labels update immediately without
    // replacing rows; capabilities are still obtained from the HA policy owner.
    if (this._drag || this._carry || this._pending || this._busy ||
        this.shadowRoot.querySelector(".entity-list")?.contains(this.shadowRoot.activeElement)) return;
    if (this._cataloguePending === null && this._catalogue.some(entity => this.entityMetadataStale(entity))) this.fetchCatalogue();
    this.fetchPreviewEntities(true);
    const selected = this.cardAt(this._selectedSlot)?.entity_id;
    if (selected?.startsWith("vacuum.") && this.profile?.schema_vacuum_area===true) { this.fetchSelectedEntity(true); return; }
    if (selected && !this._catalogue.some(entity => entity.entity_id === selected) && this.entityMetadataStale(this.entityFor(selected))) this.fetchSelectedEntity();
  }
  cacheEntityMetadata(entity,states,order) {
    if ((this._entityMetadataReads.get(entity.entity_id)?.order || 0) > order) return this.entityFor(entity.entity_id);
    this._entityIndex.set(entity.entity_id,entity); this._entityStateRefs.set(entity,states?.[entity.entity_id]);
    this._entityMetadataReads.set(entity.entity_id,{order,state:states?.[entity.entity_id],status:"loaded"});
    return entity;
  }
  fetchPreviewEntities(retryFailed=false) {
    if (!this._entryId || !this.isConnected || this._hass?.connected===false || this._drag || this._carry || this._pending || this._busy || this._profileStale || this._statusError) return [];
    const ids=new Set();
    for (const slot of this.pageSlots) {
      const card=this.cardAt(slot.slot),family=this.extraPanelFamily(card),datetime=this.isDatetimePanelAction(card),text=this.isTextPanelAction(card),camera=this.validCameraPreview(card),agenda=this.isAgendaAction(card),statistics=this.isStatisticsAction(card);
      const availability=statistics?this.statisticsAvailability(card):agenda?this.agendaAvailability(card):camera?{reason:"cameraPreview"}:text?this.textPanelAvailability(card):datetime?this.datetimePanelAvailability(card):this.extraPanelAvailability(card,family);
      if (!card?.visible || !(statistics || agenda || camera || text || datetime || this.isExtraPanelAction(card)) || !this._hass?.states?.[card.entity_id] ||
          ["extraUnsupported","datetimePanelUnsupported","textPanelUnsupported"].includes(availability.reason)) continue;
      const entity=this.entityFor(card.entity_id),read=this._entityMetadataReads.get(card.entity_id);
      if (entity && !this.entityMetadataStale(entity)) continue;
      if (!entity && read?.state===this._hass.states[card.entity_id] &&
          (read.status==="loaded" || read.status==="failed" && !retryFailed)) continue;
      ids.add(card.entity_id);
    }
    return [...ids].map(id=>this.fetchEntityMetadata(id));
  }
  fetchEntityMetadata(entityId,force=false) {
    const id=this._entryId,epoch=this._selectionEpoch,entity=this.entityFor(entityId);
    if (!id || !entityId || !this.isConnected || (!force && entity && !this.entityMetadataStale(entity))) return Promise.resolve();
    const active=this._entityMetadataRequests.get(entityId);
    if (active?.id===id && active.epoch===epoch) return active.promise;
    const pending={entityId,id,epoch,order:++this._entityMetadataOrder},states={[entityId]:this._hass?.states?.[entityId]};
    this._entityMetadataRequests.set(entityId,pending);
    this._entityMetadataReads.set(entityId,{order:pending.order,state:states?.[entityId],status:"pending"});
    pending.promise=(async()=>{
      try {
        const result=await this.ws("catalogue/get",{entry_id:id,query:entityId,limit:20});
        if (!this.isConnected || id!==this._entryId || epoch!==this._selectionEpoch || this._entityMetadataReads.get(entityId)?.order!==pending.order) return;
        // An exact preview lookup must not populate unrelated substring matches.
        const found=(result.entities || []).find(item=>item.entity_id===entityId);
        if (found) this.cacheEntityMetadata(found,states,pending.order);
        else { this._entityIndex.delete(entityId); this._entityMetadataReads.set(entityId,{order:pending.order,state:states?.[entityId],status:"loaded"}); }
        this.paintValues();
        if (this.cardAt(this._selectedSlot)?.entity_id===entityId && !this.shadowRoot.querySelector(".inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
      } catch (_ignored) {
        if (this.isConnected && id===this._entryId && epoch===this._selectionEpoch && this._entityMetadataReads.get(entityId)?.order===pending.order) {
          this._entityMetadataReads.set(entityId,{order:pending.order,state:states?.[entityId],status:"failed"}); this.paintValues();
        }
      } finally { if (this._entityMetadataRequests.get(entityId)===pending) this._entityMetadataRequests.delete(entityId); }
    })();
    return pending.promise;
  }
  async fetchSelectedEntity(force=false) {
    const entityId=this.cardAt(this._selectedSlot)?.entity_id;
    if (!entityId) return;
    const pending={entityId,id:this._entryId,epoch:this._selectionEpoch}; this._selectedEntityPending=pending;
    try { await this.fetchEntityMetadata(entityId,force); }
    finally { if (this._selectedEntityPending===pending) this._selectedEntityPending=null; }
  }
  pushHistory(before) {
    if (AEH_COMPARE(before) === AEH_COMPARE(this._draft)) return false;
    this._undo.push(before); if (this._undo.length > 60) this._undo.shift();
    this._redo = []; this._notice = ""; this._error = ""; this.scheduleDraft(); return true;
  }
  mutate(change) {
    if (!this._draft || this._busy) return false;
    const before = AEH_CLONE(this._draft), wasDirty = this.dirty; change(this._draft);
    if (!this._draft.home_order && this.profile?.carousel_order && this._draft.cards.some(card => card.slot >= 16))
      this._draft.home_order = [...this.profile.carousel_order];
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
  isDatetimeCard(card) { return typeof card?.entity_id === "string" && card.entity_id.startsWith("input_datetime."); }
  isCalendarCard(card) { return typeof card?.entity_id === "string" && card.entity_id.startsWith("calendar."); }
  isPersonCard(card) { return typeof card?.entity_id === "string" && card.entity_id.startsWith("person."); }
  isRestrictedTextCard(card) { return this.isSunCard(card) || this.isDatetimeCard(card) || this.isCalendarCard(card) || this.isPersonCard(card); }
  acceptsCard(place, card) {
    if (!place || !Array.isArray(place.types) || !place.types.includes(card?.type)) return false;
    if (this.isTileEventPanel(card)) return this.validTileEventPanel(card) && place.editable===true && place.hidden!==true && place.slot>=2;
    if (card?.action?.kind === "event") return this.profile.schema_event_actions === true && card.type === "action" && card.entity_id === "" && Object.keys(card.action).length === 1 && place.editable === true && place.hidden !== true && place.slot >= 2;
    if (this.validTextPanelAction(card) || this.validDatetimePanelAction(card) || this.validExtraPanelAction(card)) return place.editable===true && place.hidden!==true && place.slot>=2;
    if (!this.isRestrictedTextCard(card)) return true;
    const allowed = this.isPersonCard(card) ? (this.profile?.schema_person_presence===true ? this.profile?.person_text_slots : null) : this.isCalendarCard(card) && this.profile?.schema_calendar_next===true ? this.profile?.calendar_text_slots : this.isCalendarCard(card) ? null : this.isDatetimeCard(card) ? this.profile?.datetime_text_slots : this.profile?.sun_text_slots;
    return card.type === "sensor" && card.action?.kind === "none" && Object.keys(card.action).length === 1 &&
      place.editable === true && place.hidden !== true && Array.isArray(allowed) && allowed.length > 0 && allowed.length <= 14 &&
      allowed.every(Number.isInteger) && new Set(allowed).size === allowed.length && allowed.includes(place.slot);
  }
  textLayoutAllowed(layout) {
    return !Array.isArray(layout?.cards) || layout.cards.every(card => !this.isRestrictedTextCard(card) || this.acceptsCard(this.slotAt(card.slot), card));
  }
  textPlacementMessage(value) {
    const card = Array.isArray(value?.cards) ? value.cards.find(item => this.isRestrictedTextCard(item) && !this.acceptsCard(this.slotAt(item.slot),item)) : value;
    return this.t(this.isPersonCard(card) ? "personPlacement" : this.isCalendarCard(card) ? "calendarPlacement" : this.isDatetimeCard(card) ? "datetimePlacement" : "sunPlacement");
  }
  refuseTextPlacement(value=this._draft) {
    this._error = this.textPlacementMessage(value); this.paintFeedback(); this.announce(this._error); return false;
  }
  newCard(entity, slot) {
    const domain = entity.entity_id.split(".")[0];
    const information = ["sensor","binary_sensor","person","sun","input_text","input_datetime","calendar"].includes(domain);
    const action = ["scene","script","button","input_button","automation"].includes(domain);
    const icon = ({camera:"camera",vacuum:"vacuum",lawn_mower:"mower",person:"presence",calendar:"clock",sun:"clock",input_datetime:"clock",light:"light",climate:"climate",humidifier:"climate",cover:"cover",lock:"lock",alarm_control_panel:"alarm",fan:"fan",scene:"scene",switch:"switch",input_boolean:"switch"})[domain] || "action";
    return {id:`card-${AEH_UUID()}`,slot:Number(slot),type:information ? "sensor" : action ? "action" : "entity",entity_id:entity.entity_id,
      title:[...(entity.name || entity.entity_id)].slice(0,40).join(""),icon,palette:information && domain!=="person" ? "surface" : "primary",visible:true,action:{kind:information || ["camera","lawn_mower","vacuum","remote"].includes(domain) ? "none" : "default"},...(domain==="person" ? {state_color:true} : {})};
  }
  assignEntity(entityId, slot=this._selectedSlot) {
    if (this._selectingCards) return false;
    const entity = this.entityFor(entityId);
    if (!entity) return false;
    if (slot === null || slot === undefined) slot = this.pageSlots.find(item => !this.cardAt(item.slot) &&
      (!this.isRestrictedTextCard(entity) || this.acceptsCard(item,{entity_id:entity.entity_id,type:"sensor",action:{kind:"none"}})))?.slot;
    const target = this.slotAt(slot); if (!target) {
      if (this.isRestrictedTextCard(entity)) return this.refuseTextPlacement(entity);
      this.announce(this.t("chooseEmpty")); return false;
    }
    const card = this.newCard(entity,slot);
    if (!this.acceptsCard(target,card)) {
      if (this.isRestrictedTextCard(card)) return this.refuseTextPlacement(card);
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
      if (this.isRestrictedTextCard(source) || this.isRestrictedTextCard(other)) return this.refuseTextPlacement(this.isRestrictedTextCard(source) ? source : other);
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
    return !!place && (!moving || !!ownSlots) && (!this.cardAt(slot) || !!ownSlots?.has(slot)) && this.acceptsCard(place,card) && (card.action?.kind !== "control" || this._draft.version===3 && (this.validTextPanelAction(card) || this.validDatetimePanelAction(card) || this.validActionPanelAction(card) || this.validExtraPanelAction(card)) && place.editable && !place.hidden && place.slot>=2 ||
      (this._draft.version === 3 && card.type === "entity" && ((card.action.control === "light" && card.entity_id.startsWith("light.") && (!Object.hasOwn(card.action,"detail") || this.validDetailAction(card))) || (card.action.control === "number" && (this.isNumberEntity(card) || ["position","tilt_position"].includes(card.action.property) && card.entity_id.startsWith("cover.") || card.action.property==="color_temp_kelvin" && card.entity_id.startsWith("light.") || card.action.property==="temperature" && card.entity_id.startsWith("climate.") || card.action.property==="humidity" && (card.entity_id.startsWith("humidifier.") || card.entity_id.startsWith("climate.")))) || (card.action.control === "choice" && (this.isChoiceEntity(card) || ["hvac_mode","preset_mode","fan_mode","swing_mode","swing_horizontal_mode"].includes(card.action.property) && card.entity_id.startsWith("climate.") || card.action.property==="mode" && card.entity_id.startsWith("humidifier.") || card.action.property==="effect" && card.entity_id.startsWith("light.") || card.action.property==="fan_speed" && card.entity_id.startsWith("vacuum.") || card.action.property==="activity" && card.entity_id.startsWith("remote."))) || (card.action.control === "cover" && card.entity_id.startsWith("cover.")) || (card.action.control === "fan" && card.entity_id.startsWith("fan.")) || (card.action.control === "humidifier" && card.entity_id.startsWith("humidifier.")) || (card.action.control === "robot" && ["vacuum","lawn_mower"].includes(card.entity_id.split(".")[0])) || (card.action.control === "panel" && (this.validPanelAction(card) || this.validDetailAction(card) || this.validMediaPanelAction(card))))));
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
    if (!this.textLayoutAllowed(this._draft)) return this.refuseTextPlacement();
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
    if (!this.textLayoutAllowed(backup.layout)) throw new Error(this.textPlacementMessage(backup.layout));
    this._statusRequest++;
    const id = this._entryId, epoch = this._selectionEpoch, revision = this._saved.revision;
    const result = await this.ws("layout/import",{entry_id:id,expected_revision:revision,backup,dry_run:true});
    if (id !== this._entryId || epoch !== this._selectionEpoch || revision !== this._saved.revision) return false;
    if (!this.textLayoutAllowed(result.layout)) throw new Error(this.textPlacementMessage(result.layout));
    this._pending = {kind:"import",layout:result.layout,warnings:result.warnings || []}; this.renderModal(); return true;
  }
  useImported() {
    if (this._pending?.kind !== "import") return;
    if (!this.textLayoutAllowed(this._pending.layout)) { this.refuseTextPlacement(this._pending.layout); return; }
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
  isNumberEntity(card) { return ["number","input_number"].includes(card?.entity_id?.split(".")[0]); }
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
    const action = actions.find(item => item && typeof item === "object" && item.service === `${card?.entity_id?.split(".")[0]}.set_value`);
    if (!card || card.type !== "entity" || !card.visible || !slot?.editable || slot.hidden
      || !this.isNumberEntity(card) || entity?.domain !== card.entity_id.split(".")[0] || entity.available !== true
      || !state || ["unknown","unavailable"].includes(state.state) || !action || !descriptor || descriptor.schema !== "numeric_steps_v1"
      || !Number.isInteger(entity.number_control.index) || !attrs) return {ready:false,reason:"numberEntity"};
    // Server metadata is canonical and bounded by NumericDomain. This fingerprint
    // only detects a changed review; backend dispatch revalidates authoritative data.
    return {ready:true,reason:"numberHint",caps:{domain:descriptor,metadata:{min:attrs.min,max:attrs.max,step:attrs.step,unit:attrs.unit_of_measurement ?? ""}}};
  }
  validDetailAction(card) {
    const action=card?.action,domain=card?.entity_id?.split(".")[0];
    if (action?.kind!=="control" || !this.profile?.layout_versions?.includes(3)) return false;
    if (domain==="light") return this.profile.schema_light_detail===true && this.profile.schema_control_types?.includes("light") &&
      action.control==="light" && action.detail===1 && Object.keys(action).length===3;
    return domain==="climate" && this.profile.schema_climate_panel===true && this.profile.schema_control_types?.includes("panel") &&
      action.control==="panel" && action.property==="climate" && Object.keys(action).length===3;
  }
  detailControlAvailability(card=this.cardAt(this._selectedSlot),family=card?.entity_id?.split(".")[0]) {
    const unsupported={ready:false,reason:"detailUnsupported"},unavailable={ready:false,reason:"detailEntity"};
    const climate=family==="climate",flag=climate?"climate_panel":"light_detail",kind=climate?"panel":"light";
    if (!["light","climate"].includes(family) || !this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
        this._status?.device_available!==true || this._status.entity_control_status!=="ready" || this._status.detail_version!==1 ||
        this._status[flag+"_version"]!==1 || !this._status.native_control_types?.includes("entity_control_v1") ||
        !this._status.control_kinds?.includes(kind) || this.profile?.["schema_"+flag]!==true ||
        !this.profile.schema_control_types?.includes(kind) || !this.profile.layout_versions?.includes(3)) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id],meta=entity?.[flag];
    const names=climate?["temperature","humidity","hvac_mode","preset_mode","fan_mode","swing_mode","swing_horizontal_mode"]:["color_temp_kelvin","effect"];
    const reasons=meta?.facet_reasons;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || slot.slot<2 ||
        card.entity_id.split(".")[0]!==family || entity?.domain!==family || !state ||
        (!climate && (entity.available!==true || !["on","off"].includes(state.state))) ||
        (climate && !["off","heat","cool","heat_cool","auto","dry","fan_only","unknown","unavailable"].includes(state.state)) ||
        meta?.version!==1 || !Number.isInteger(meta.facets) || meta.facets<0 || meta.facets>(climate?127:3) ||
        !/^[0-9a-f]{64}$/.test(meta.fingerprint) || !reasons || typeof reasons!=="object" || Array.isArray(reasons) ||
        Object.entries(reasons).some(([key,value])=>!names.includes(key) || !["unsupported_metadata","unsupported_service","unsupported_catalogue"].includes(value)) ||
        !meta.state || typeof meta.state!=="object" || Array.isArray(meta.state)) return unavailable;
    const fields=climate?["supported_features","min_temp","max_temp","target_temp_step","hvac_modes","preset_modes","fan_modes","swing_modes","swing_horizontal_modes","min_humidity","max_humidity","target_humidity_step"]:
      ["supported_features","supported_color_modes","min_color_temp_kelvin","max_color_temp_kelvin","effect_list"];
    const observedMetadata=Object.fromEntries(fields.map(key=>[key,state.attributes?.[key]??null]));
    if (climate) observedMetadata.temperatureUnit=this._hass?.config?.unit_system?.temperature??null;
    return {ready:true,reason:climate?"climatePanelHint":"lightDetailHint",missingFacets:Object.keys(reasons),
      caps:{family,facets:meta.facets,fingerprint:meta.fingerprint,reasons,observedMetadata}};
  }
  isTextPanelAction(card) {
    const a=card?.action;
    return card?.entity_id?.startsWith("input_text.") && card.type==="entity" && a?.kind==="control" &&
      a.control==="panel" && a.property==="text" && Object.keys(a).length===3;
  }
  validTextPanelAction(card) {
    return this.isTextPanelAction(card) && this.profile?.layout_versions?.includes(3) &&
      this.profile?.schema_control_types?.includes("panel") && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"text");
  }
  textPanelBounds(min,max) { return Number.isInteger(min) && Number.isInteger(max) && min>=0 && max>=1 && min<=max && max<=255; }
  textPanelValueReason(value,min=0,max=255) {
    if(typeof value!=="string" || [...value].some(c=>c.codePointAt(0)>=0xD800 && c.codePointAt(0)<=0xDFFF)) return "encoding";
    if([...value].length<min || [...value].length>max || [...value].length>255 || new TextEncoder().encode(value).length>1020) return "length";
    return /^[\x20-\x7EĄąĆćĘęŁłŃńÓóŚśŹźŻż]*$/u.test(value)?"none":"characters";
  }
  textPanelMetadata(card) {
    const m=this.entityFor(card?.entity_id)?.text_panel;
    const exact=(v,keys)=>v && typeof v==="object" && !Array.isArray(v) && Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k));
    if(!card?.entity_id?.startsWith("input_text.") || !exact(m,["version","panel_type","caps","fingerprint","state","available","eligible_actions"]) ||
      m.version!==1 || m.panel_type!=="text" || typeof m.fingerprint!=="string" || !/^[0-9a-f]{64}$/.test(m.fingerprint)) return null;
    const c=m.caps,o=m.state,bounds=this.textPanelBounds(c?.min,c?.max),known=o?.source==="known";
    if(!exact(c,["min","max","can_set"]) || typeof c.can_set!=="boolean" || !bounds && !(c.min===null && c.max===null && !c.can_set) ||
      !exact(o,["source","value","reason"]) || !["known","unknown","unavailable","unsupported"].includes(o.source) ||
      !["none","password","mode","pattern","bounds","length","encoding","characters"].includes(o.reason) ||
      m.available!==known || m.eligible_actions!==(known&&c.can_set?1:0)) return null;
    if(o.source!=="unsupported") {
      if(!bounds || o.reason!=="none" || (known ? this.textPanelValueReason(o.value,c.min,c.max)!=="none" || ["unknown","unavailable"].includes(o.value) : o.value!==null)) return null;
    } else if(o.reason==="none" || o.value!==null || ["password","mode","pattern","bounds"].includes(o.reason)&&c.can_set ||
      o.reason==="bounds"&&bounds || ["length","encoding","characters"].includes(o.reason)&&!bounds) return null;
    return m;
  }
  textPanelLive(live) {
    const a=live?.attributes,bounds=this.textPanelBounds(a?.min,a?.max),mode=a?.mode;
    const reason=mode==="password"?"password":mode!=="text"?"mode":a.pattern!=null?"pattern":!bounds?"bounds":"none";
    const services=this._hass?.services?.input_text;
    const caps={min:bounds?a.min:null,max:bounds?a.max:null,can_set:reason==="none" && !!services && typeof services==="object" && !Array.isArray(services) && Object.hasOwn(services,"set_value")};
    // Privacy precedes reading live.state, including stale catalogue metadata.
    if(reason!=="none") return {caps,state:{source:"unsupported",value:null,reason}};
    const raw=live.state;
    if(["unknown","unavailable"].includes(raw)) return {caps,state:{source:raw,value:null,reason:"none"}};
    const invalid=this.textPanelValueReason(raw,a.min,a.max);
    return {caps,state:invalid==="none"?{source:"known",value:raw,reason:"none"}:{source:"unsupported",value:null,reason:invalid}};
  }
  textPanelAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"textPanelUnsupported"},invalid={ready:false,reason:"textPanelEntity"};
    if(!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
      this._status?.device_available!==true || this._status.entity_control_status!=="ready" || !this._status.native_control_types?.includes("entity_control_v1") ||
      !this._status.control_kinds?.includes("panel") || !this.profile?.schema_control_types?.includes("panel") || !this.profile.layout_versions?.includes(3) ||
      !this.hasExtraProfile(this.profile.schema_panel_extra_profiles,"text") || !this.hasExtraProfile(this._status.panel_extra_profiles,"text")) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),live=this._hass?.states?.[card?.entity_id],meta=this.textPanelMetadata(card),a=card?.action;
    if(!card || !["entity","sensor"].includes(card.type) || !card.visible || !slot?.editable || slot.hidden || slot.slot<2 || !slot.types?.includes("entity") ||
      !card.entity_id?.startsWith("input_text.") || entity?.domain!=="input_text" || !live || !meta ||
      !(["none","default"].includes(a?.kind) && Object.keys(a).length===1) && !this.isTextPanelAction(card) ||
      !this._hass.services || typeof this._hass.services!=="object" || Array.isArray(this._hass.services)) return invalid;
    const actual=this.textPanelLive(live);
    if(JSON.stringify(actual.caps)!==JSON.stringify(meta.caps) || this.entityMetadataStale(entity)) return invalid;
    return {ready:true,reason:meta.caps.can_set?"textPanelHint":"textPanelPassive",caps:{...meta.caps,fingerprint:meta.fingerprint}};
  }
  textPanelPreview(card) {
    const live=this._hass?.states?.[card?.entity_id];
    if(this._hass?.connected===false || !live) return {message:this.t("offline")};
    const actual=this.textPanelLive(live);
    if(["password","mode"].includes(actual.state.reason)) return {message:this.t("textPanelHidden")};
    if(this.textPanelAvailability(card).reason==="textPanelUnsupported") return {message:this.t("textPanelUnsupported")};
    const m=this.textPanelMetadata(card),entity=this.entityFor(card?.entity_id);
    if(!m || this.entityMetadataStale(entity) || JSON.stringify(actual.caps)!==JSON.stringify(m.caps) || JSON.stringify(actual.state)!==JSON.stringify(m.state)) return {message:this.t("extraRefreshing")};
    if(m.state.source!=="known") return {message:this.t(m.state.source==="unknown"?"unknown":m.state.source==="unavailable"?"offline":({pattern:"textPanelPattern",bounds:"textPanelBounds",length:"textPanelLength",encoding:"textPanelCharacters",characters:"textPanelCharacters"})[m.state.reason]||"textPanelHidden")};
    return {meta:m,observation:m.state,message:m.state.value || this.t("textPanelEmpty")};
  }
  textPanelPreviewMarkup(card) {
    if(!this.isTextPanelAction(card)) return "";
    const p=this.textPanelPreview(card);
    return `<section data-text-panel-preview>${this.icon("mdi:form-textbox")}<h3>${this.t("extraPreview")}</h3><p style="white-space:pre-wrap;overflow-wrap:anywhere">${AEH_ESCAPE(p.message)}</p>`+
      (p.observation?`<p>${[...p.observation.value].length} / ${p.meta.caps.max}</p>`:"")+`<p class="hint">${this.t("extraPreviewNote")}</p></section>`;
  }
  isDatetimePanelAction(card) {
    const a=card?.action;
    return this.isDatetimeCard(card) && card.type==="entity" && a?.kind==="control" && a.control==="panel" &&
      a.property==="datetime" && Object.keys(a).length===3;
  }
  validDatetimePanelAction(card) {
    return this.isDatetimePanelAction(card) && this.profile?.layout_versions?.includes(3) &&
      this.profile?.schema_control_types?.includes("panel") && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"datetime");
  }
  datetimeTupleValid(value,mode,known=true) {
    const fields=["year","month","day","hour","minute","second"],mask=({date:7,time:56,datetime:63})[mode];
    if(!mask || !value) return false;
    const bounds=[[1,9999],[1,12],[1,31],[0,23],[0,59],[0,59]];
    if(!fields.every((key,i)=>known && (mask&(1<<i)) ? Number.isInteger(value[key]) && value[key]>=bounds[i][0] && value[key]<=bounds[i][1] : value[key]===null)) return false;
    if(!known || !(mask&1)) return true;
    const y=value.year,days=[31,y%4===0&&(y%100!==0||y%400===0)?29:28,31,30,31,30,31,31,30,31,30,31];
    return value.day<=days[value.month-1];
  }
  datetimePanelMetadata(card) {
    const m=this.entityFor(card?.entity_id)?.datetime_panel;
    const exact=(v,keys)=>v && typeof v==="object" && !Array.isArray(v) && Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k));
    const text=(v,max)=>typeof v==="string" && new TextEncoder().encode(v).length<=max && !/[\p{C}\p{Zl}\p{Zp}]/u.test(v);
    if(!this.isDatetimeCard(card) || !exact(m,["version","panel_type","caps","fingerprint","state","available","eligible_actions"]) ||
      m.version!==1 || m.panel_type!=="datetime" || typeof m.fingerprint!=="string" || !/^[0-9a-f]{64}$/.test(m.fingerprint)) return null;
    const c=m.caps,o=m.state,known=o?.source==="known";
    if(!exact(c,["mode","can_set","zone_text"]) || !["date","time","datetime"].includes(c.mode) || typeof c.can_set!=="boolean" ||
      !text(c.zone_text,48) || c.mode!=="datetime" && c.zone_text!=="" ||
      !exact(o,["source","year","month","day","hour","minute","second","updated_text"]) || !["known","unknown","unavailable"].includes(o.source) ||
      !text(o.updated_text,25) || o.updated_text!=="" && !this.contextDateParts(o.updated_text) ||
      !this.datetimeTupleValid(o,c.mode,known) || m.available!==known || m.eligible_actions!==(known&&c.can_set?1:0)) return null;
    return m;
  }
  datetimePanelAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"datetimePanelUnsupported"},invalid={ready:false,reason:"datetimePanelEntity"};
    if(!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
      this._status?.device_available!==true || this._status.entity_control_status!=="ready" || !this._status.native_control_types?.includes("entity_control_v1") ||
      !this._status.control_kinds?.includes("panel") || !this.profile?.schema_control_types?.includes("panel") || !this.profile.layout_versions?.includes(3) ||
      !this.hasExtraProfile(this.profile.schema_panel_extra_profiles,"datetime") || !this.hasExtraProfile(this._status.panel_extra_profiles,"datetime")) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),live=this._hass?.states?.[card?.entity_id],meta=this.datetimePanelMetadata(card),a=card?.action;
    const passive=["none","default"].includes(a?.kind) && Object.keys(a).length===1;
    if(!card || !["entity","sensor"].includes(card.type) || !card.visible || !slot?.editable || slot.hidden || slot.slot<2 ||
      !slot.types?.includes("entity") || !this.isDatetimeCard(card) || entity?.domain!=="input_datetime" || !live || !meta ||
      (!passive && !this.isDatetimePanelAction(card))) return invalid;
    const attrs=live.attributes;
    if(typeof attrs?.has_date!=="boolean" || typeof attrs?.has_time!=="boolean" || !attrs.has_date&&!attrs.has_time ||
      !this._hass?.services || typeof this._hass.services!=="object" || Array.isArray(this._hass.services)) return invalid;
    const mode=attrs.has_date?(attrs.has_time?"datetime":"date"):"time",services=this._hass.services.input_datetime;
    const canSet=!!services && typeof services==="object" && !Array.isArray(services) && Object.hasOwn(services,"set_datetime");
    if(meta.caps.mode!==mode || meta.caps.can_set!==canSet) return invalid;
    // Configuration review depends on capabilities, not changing observed values or zone text.
    return {ready:true,reason:canSet?"datetimePanelHint":"datetimePanelPassive",caps:{mode,can_set:canSet,fingerprint:meta.fingerprint}};
  }
  datetimeObservedTuple(live,mode) {
    const raw=live?.state,fields=["year","month","day","hour","minute","second"];
    if(typeof raw!=="string" || raw.length>19) return null;
    const pattern=mode==="date"?/^([0-9]{1,4})-([0-9]{2})-([0-9]{2})$/:mode==="time"?/^([0-9]{2}):([0-9]{2}):([0-9]{2})$/:/^([0-9]{1,4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})$/;
    const match=raw.match(pattern);if(!match || match[0]!==raw) return null;
    const values=match.slice(1).map(Number),mask=({date:7,time:56,datetime:63})[mode],tuple={};
    let next=0;
    for(let i=0;i<fields.length;i++) {
      const key=fields[i];tuple[key]=(mask&(1<<i))?values[next++]:null;
      if((mask&(1<<i)) && (!Number.isInteger(live.attributes?.[key]) || live.attributes[key]!==tuple[key])) return null;
    }
    return this.datetimeTupleValid(tuple,mode)?tuple:null;
  }
  datetimePanelPreview(card) {
    const meta=this.datetimePanelMetadata(card),entity=this.entityFor(card?.entity_id),live=this._hass?.states?.[card?.entity_id];
    if(this._hass?.connected===false || !live || live.state==="unavailable") return {message:this.t("offline")};
    if(live.state==="unknown") return {message:this.t("unknown")};
    if(this.datetimePanelAvailability(card).reason==="datetimePanelUnsupported") return {message:this.t("datetimePanelUnsupported")};
    if(!meta) {
      const read=this._entityMetadataReads.get(card?.entity_id),current=read?.state===live;
      return {message:this.t(entity || current&&read?.status==="loaded"?"datetimePanelEntity":current&&read?.status==="failed"?"extraLoadFailed":"extraLoading")};
    }
    const o=meta.state,c=meta.caps,attrs=live.attributes,mode=typeof attrs?.has_date==="boolean"&&typeof attrs?.has_time==="boolean"&&
      (attrs.has_date||attrs.has_time)?(attrs.has_date?(attrs.has_time?"datetime":"date"):"time"):null;
    if(mode!==c.mode || entity.state!==live.state || this.entityMetadataStale(entity)) return {message:this.t("extraRefreshing")};
    if(live.last_updated && (!o.updated_text || !Number.isFinite(Date.parse(live.last_updated)) ||
      Math.floor(Date.parse(live.last_updated)/1000)!==Math.floor(Date.parse(o.updated_text)/1000))) return {message:this.t("extraRefreshing")};
    if(o.source!=="known") return {message:this.t(o.source==="unavailable"?"offline":"unknown")};
    const tuple=this.datetimeObservedTuple(live,c.mode);
    if(!tuple || Object.keys(tuple).some(k=>tuple[k]!==o[k])) return {message:this.t("extraRefreshing")};
    const pad=v=>String(v).padStart(2,"0"),date=c.mode!=="time"?this.calendarDateText(`${String(o.year).padStart(4,"0")}-${pad(o.month)}-${pad(o.day)}`):"";
    const clock=c.mode!=="date"?`${pad(o.hour)}:${pad(o.minute)}:${pad(o.second)}`:"";
    return {meta,observation:o,message:[date,clock].filter(Boolean).join(" ")};
  }
  datetimePanelPreviewMarkup(card) {
    if(!this.isDatetimePanelAction(card)) return "";
    const p=this.datetimePanelPreview(card),zone=p.observation?p.meta.caps.zone_text:"";
    return `<section data-datetime-panel-preview>${this.icon("clock")}<h3>${this.t("extraPreview")}</h3><p>${AEH_ESCAPE(p.message)}</p>`+
      (zone?`<p>${this.t("extraZone")}: ${AEH_ESCAPE(zone)}</p>`:"")+
      (p.observation?.updated_text?`<p>${this.t("extraUpdated")}: ${AEH_ESCAPE(this.contextDateText("value",p.observation.updated_text))}</p>`:"")+
      `<p class="hint">${this.t("datetimePanelWallHint")}</p><p class="hint">${this.t("extraPreviewNote")}</p></section>`;
  }
  isAgendaAction(card) {
    const a=card?.action;
    return ["sensor","entity"].includes(card?.type) && card?.entity_id?.startsWith("calendar.") && a?.kind==="control" && a.control==="panel" && a.property==="agenda" && Object.keys(a).length===3;
  }
  validAgendaAction(card) {
    return this.isAgendaAction(card) && this.profile?.schema_info_agenda_version===1 && this.profile?.layout_versions?.includes(3) && this.profile?.schema_control_types?.includes("panel");
  }
  agendaAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"agendaUnavailable"};
    if(!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
       this._status.device_available!==true || this._status.entity_control_status!=="ready" ||
       !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("panel") ||
       this._status.info_agenda_version!==1 || this.profile?.schema_info_agenda_version!==1 ||
       !this.hasExtraProfile(this._status.panel_extra_profiles,"info") || !this.profile?.layout_versions?.includes(3) ||
       !this.profile?.schema_control_types?.includes("panel")) return unsupported;
    const place=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),meta=entity?.agenda,live=this._hass?.states?.[card?.entity_id];
    if(!card || !["sensor","entity"].includes(card.type) || !card.visible || !place?.editable || place.hidden || place.slot<2 ||
       !card.entity_id.startsWith("calendar.") || entity?.domain!=="calendar" || !live || this.entityMetadataStale(entity) ||
       !meta || Array.isArray(meta) || Object.keys(meta).length!==2 || meta.version!==1 || meta.read_only!==true) return unsupported;
    return {ready:true,reason:"agendaHint",caps:{agendaVersion:1,entityId:card.entity_id}};
  }
  isStatisticsAction(card) {
    const a=card?.action;
    return ["sensor","entity"].includes(card?.type) && card?.entity_id?.startsWith("sensor.") && a?.kind==="control" && a.control==="panel" && a.property==="statistics" && Object.keys(a).length===3;
  }
  validStatisticsAction(card) {
    return this.isStatisticsAction(card) && this.profile?.schema_info_statistics_version===1 && this.profile?.layout_versions?.includes(3) && this.profile?.schema_control_types?.includes("panel");
  }
  statisticsAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"statisticsUnavailable"};
    if(!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
       this._status.device_available!==true || this._status.entity_control_status!=="ready" ||
       !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("panel") ||
       this._status.info_statistics_version!==1 || this.profile?.schema_info_statistics_version!==1 ||
       !this.hasExtraProfile(this._status.panel_extra_profiles,"info") || !this.profile?.layout_versions?.includes(3) ||
       !this.profile?.schema_control_types?.includes("panel")) return unsupported;
    const place=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),meta=entity?.statistics,live=this._hass?.states?.[card?.entity_id];
    if(!card || !["sensor","entity"].includes(card.type) || !card.visible || !place?.editable || place.hidden || place.slot<2 ||
       !card.entity_id.startsWith("sensor.") || entity?.domain!=="sensor" || !live || this.entityMetadataStale(entity) ||
       !meta || Array.isArray(meta) || Object.keys(meta).length!==3 || meta.version!==1 || meta.read_only!==true || meta.hours!==24) return unsupported;
    return {ready:true,reason:"statisticsHint",caps:{statisticsVersion:1,entityId:card.entity_id}};
  }
  extraPanelFamily(card) {
    const domain=card?.entity_id?.split(".")[0];
    return domain==="lock" ? "lock" : ["sensor","binary_sensor","calendar","alarm_control_panel","person","sun"].includes(domain) ? "info" : null;
  }
  actionPanelDomain(card) {
    const domain=card?.entity_id?.split(".")[0];
    return ["button","input_button","scene","script","automation"].includes(domain)?domain:null;
  }
  isActionPanelAction(card) {
    const a=card?.action,domain=this.actionPanelDomain(card),automation=domain==="automation";
    return !!domain && ["entity","action"].includes(card?.type) && a?.kind==="control" && a.control==="panel" && a.property==="action" &&
      Object.keys(a).length===(automation?5:3) && (!automation || typeof a.skip_condition==="boolean" && typeof a.stop_actions==="boolean");
  }
  validActionPanelAction(card) {
    return this.isActionPanelAction(card) && this.profile?.layout_versions?.includes(3) &&
      this.profile?.schema_control_types?.includes("panel") && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"action");
  }
  isActionParametersAction(card) {
    const a=card?.action;
    return card?.entity_id?.startsWith("script.") && ["entity","action"].includes(card?.type) &&
      a?.kind==="control" && a.control==="panel" && a.property==="action" && a.parameters==="boolean_v1" && Object.keys(a).length===4;
  }
  validActionParametersAction(card) {
    return this.isActionParametersAction(card) && this.profile?.schema_action_parameters_version===1 &&
      this.profile?.layout_versions?.includes(3) && this.profile?.schema_control_types?.includes("panel") &&
      this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"action");
  }
  actionPanelPolicies(card) {
    if (this.actionPanelDomain(card)!=="automation") return null;
    if (this.isActionPanelAction(card)) return {skip_condition:card.action.skip_condition,stop_actions:card.action.stop_actions};
    const a=card?.action, policies={skip_condition:false,stop_actions:false};
    // Preserve the actual legacy service defaults during explicit conversion.
    if (a?.kind==="service" && ["automation.trigger","automation.turn_off"].includes(a.service)) {
      const key=a.service==="automation.trigger"?"skip_condition":"stop_actions", value=Object.hasOwn(a.data || {},key)?a.data[key]:true;
      if (typeof value!=="boolean") return null;
      policies[key]=value;
    }
    return policies;
  }
  actionPanelConversionAllowed(card) {
    if(this.isActionPanelAction(card) || this.isActionParametersAction(card)) return true;
    const a=card?.action,domain=this.actionPanelDomain(card);
    if(["default","none"].includes(a?.kind)) return Object.keys(a).length===1;
    if(a?.kind!=="service" || !a.data || typeof a.data!=="object" || Array.isArray(a.data)) return false;
    const services={button:["press"],input_button:["press"],scene:["turn_on"],script:["turn_on","turn_off"],automation:["turn_on","turn_off","trigger"]};
    if(!services[domain]?.some(name=>a.service===domain+"."+name)) return false;
    const allowed=a.service==="automation.trigger"?["skip_condition"]:a.service==="automation.turn_off"?["stop_actions"]:[];
    return Object.keys(a.data).every(key=>allowed.includes(key) && typeof a.data[key]==="boolean");
  }
  actionPanelMetadata(card) {
    return this.parseActionPanelMetadata(card,this.entityFor(card?.entity_id)?.action_panel,false);
  }
  actionParametersMetadata(card) {
    return this.parseActionPanelMetadata(card,this.entityFor(card?.entity_id)?.action_parameters,true);
  }
  parseActionPanelMetadata(card,meta,parameters) {
    const domain=this.actionPanelDomain(card);
    const exact=(v,keys)=>v && typeof v==="object" && !Array.isArray(v) && Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k));
    const masks={button:1,input_button:1,scene:2,script:12,automation:112};
    if (!domain || !exact(meta,["version","panel_type","caps","fingerprint","state","available","eligible_actions"]) ||
      meta.version!==1 || meta.panel_type!=="action" || typeof meta.fingerprint!=="string" || !/^[0-9a-f]{64}$/.test(meta.fingerprint)) return null;
    const c=meta.caps,o=meta.state;
    const parameterKeys=parameters?["parameters_version","parameter_status","parameter_label","parameter_default"]:[];
    if(parameters && (domain!=="script" || !c || c.parameters_version!==1 ||
      !["ready","unsupported","metadata_unavailable"].includes(c.parameter_status) || typeof c.parameter_label!=="string" ||
      new TextEncoder().encode(c.parameter_label).length>96 || /[\p{C}\p{Zl}\p{Zp}]/u.test(c.parameter_label) ||
      (c.parameter_default!==null && typeof c.parameter_default!=="boolean") ||
      (c.parameter_status==="ready" ? !c.parameter_label.trim() : c.parameter_label!=="" || c.parameter_default!==null) ||
      c.run_blocked!==(!(c.operations&4)?"service_unavailable":c.parameter_status==="ready"?"none":c.parameter_status==="unsupported"?"needs_parameters":"metadata_unavailable"))) return null;
    if (!exact(c,["action_type","operations","skip_condition","stop_actions","run_blocked",...parameterKeys]) || c.action_type!==domain ||
      !Number.isInteger(c.operations) || c.operations<0 || c.operations>127 || (c.operations&~masks[domain]) ||
      (domain==="automation" ? c.skip_condition!==false || c.stop_actions!==false : c.skip_condition!==null || c.stop_actions!==null) ||
      !["none","needs_parameters","metadata_unavailable","service_unavailable"].includes(c.run_blocked) ||
      (domain!=="script" && c.run_blocked!=="none") || (domain==="script" && Boolean(c.operations&4)===(c.run_blocked==="service_unavailable")) ||
      !exact(o,["source","phase","last_used_status","last_used_text","current"]) || !["known","unknown","unavailable"].includes(o.source) ||
      !["value","unknown","invalid","too_long"].includes(o.last_used_status) || typeof o.last_used_text!=="string" ||
      new TextEncoder().encode(o.last_used_text).length>48 || /[\p{C}\p{Zl}\p{Zp}]/u.test(o.last_used_text) ||
      (o.last_used_status==="value")!==Boolean(o.last_used_text) ||
      (o.current!==null && (!Number.isInteger(o.current) || o.current<0 || o.current>65535 || !["script","automation"].includes(domain)))) return null;
    if(o.last_used_status==="value" && (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?[+-]\d{2}:\d{2}$/.test(o.last_used_text) || !Number.isFinite(Date.parse(o.last_used_text)))) return null;
    const known=o.source==="known",phases={button:["stateless"],input_button:["stateless"],scene:["stateless"],script:["idle","running"],automation:["enabled","disabled"]};
    if (!(known?phases[domain]:["unknown"]).includes(o.phase) || meta.available!==known ||
      (!known && (o.last_used_status!=="unknown" || o.last_used_text!=="" || o.current!==null))) return null;
    let eligible=0;
    if(known) eligible=["button","input_button","scene"].includes(domain)?c.operations:domain==="script"?
      ((o.phase==="running"?8:c.run_blocked==="none"?4:0)&c.operations):((64|(o.phase==="disabled"?16:32))&c.operations);
    if(!Number.isInteger(meta.eligible_actions) || meta.eligible_actions!==eligible) return null;
    return meta;
  }
  actionPanelAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"actionPanelUnsupported"},invalid={ready:false,reason:"actionPanelEntity"};
    if (!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
      this._status?.device_available!==true || this._status.entity_control_status!=="ready" || !this._status.native_control_types?.includes("entity_control_v1") ||
      !this._status.control_kinds?.includes("panel") || !this.profile?.schema_control_types?.includes("panel") || !this.profile.layout_versions?.includes(3) ||
      !this.hasExtraProfile(this.profile.schema_panel_extra_profiles,"action") || !this.hasExtraProfile(this._status.panel_extra_profiles,"action")) return unsupported;
    if(!this.actionPanelConversionAllowed(card)) return {ready:false,reason:"actionPanelLegacyData"};
    const slot=this.slotAt(card?.slot),domain=this.actionPanelDomain(card),entity=this.entityFor(card?.entity_id),meta=this.actionPanelMetadata(card);
    if(!card || !["entity","action"].includes(card.type) || !card.visible || !slot?.editable || slot.hidden || slot.slot<2 ||
      !domain || entity?.domain!==domain || !this._hass?.states?.[card.entity_id] || !meta) return invalid;
    const definitions={button:[["press",1]],input_button:[["press",1]],scene:[["turn_on",2]],script:[["turn_on",4],["turn_off",8]],automation:[["turn_on",16],["turn_off",32],["trigger",64]]};
    const services=this._hass?.services?.[domain];
    if(!services || typeof services!=="object" || Array.isArray(services)) return invalid;
    const operations=definitions[domain].reduce((mask,[service,bit])=>mask|(Object.hasOwn(services,service)?bit:0),0),policies=this.actionPanelPolicies(card);
    if(operations!==meta.caps.operations || domain==="automation" && !policies) return invalid;
    // Catalogue fingerprint remains unmodified. Saved/staged policies are separate.
    // Timestamps/current/phase are telemetry, not capability-review freshness.
    return {ready:true,reason:"actionPanelHint",caps:{catalogue:meta.caps,fingerprint:meta.fingerprint,effectivePolicies:policies}};
  }
  actionParametersAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"actionParametersUnsupported"},invalid={ready:false,reason:"actionParametersEntity"};
    if(!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
      this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("panel") ||
      this.profile?.schema_action_parameters_version!==1 || this._status.action_parameters_version!==1 ||
      !this.profile.layout_versions?.includes(3) || !this.profile.schema_control_types?.includes("panel") ||
      !this.hasExtraProfile(this.profile.schema_panel_extra_profiles,"action") || !this.hasExtraProfile(this._status.panel_extra_profiles,"action")) return unsupported;
    if(!this.actionPanelConversionAllowed(card)) return {ready:false,reason:"actionPanelLegacyData"};
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),meta=this.actionParametersMetadata(card);
    if(!card || !["entity","action"].includes(card.type) || !card.visible || !slot?.editable || slot.hidden || slot.slot<2 ||
      entity?.domain!=="script" || !this._hass?.states?.[card.entity_id] || !meta || meta.caps.parameter_status!=="ready") return invalid;
    // HA captures the actual registered direct script service. Entity suffixes can be renamed independently.
    const services=this._hass?.services?.script;
    if(!services || typeof services!=="object" || Array.isArray(services) || Boolean(meta.caps.operations&8)!==Object.hasOwn(services,"turn_off")) return invalid;
    return {ready:true,reason:"actionParametersHint",caps:{catalogue:meta.caps,fingerprint:meta.fingerprint}};
  }
  actionParametersPreviewMarkup(card) {
    const meta=this.actionParametersMetadata(card);
    if(!meta || meta.caps.parameter_status!=="ready") return "";
    const c=meta.caps;
    return `<section data-action-parameters-preview><p class="hint">${AEH_ESCAPE(c.parameter_label)}<br>${this.t(c.parameter_default===null?"actionParametersNoDefault":c.parameter_default?"actionParametersDefaultYes":"actionParametersDefaultNo")}</p></section>`;
  }
  actionPanelIcon(card) {
    return ({button:"mdi:gesture-tap-button",input_button:"mdi:gesture-tap-button",scene:"mdi:palette-outline",script:"mdi:script-text-outline",automation:"mdi:robot"})[this.actionPanelDomain(card)] || "action";
  }
  actionPanelPolicyMarkup(card,policies=this.actionPanelPolicies(card),editable=false) {
    if(this.actionPanelDomain(card)!=="automation" || !policies) return "";
    if(editable) return `<section data-action-panel-policies><label><input type="checkbox" data-field="action-policy-skip_condition" ${policies.skip_condition?"checked":""}>${this.t("skipConditions")}</label><label><input type="checkbox" data-field="action-policy-stop_actions" ${policies.stop_actions?"checked":""}>${this.t("stopActions")}</label>${this.actionPanelPolicyMarkup(card,policies)}</section>`;
    return `<p class="hint" data-action-panel-policy>${this.t(policies.skip_condition?"actionPanelSkipConditions":"actionPanelCheckConditions")}<br>${this.t(policies.stop_actions?"actionPanelStopRunning":"actionPanelKeepRunning")}</p>`;
  }
  actionLastUsedText(value) {
    // Preserve HA's local wall time, complete fractional seconds and explicit offset.
    // Date/Intl conversion would round microseconds and may substitute the browser zone.
    const m=typeof value==="string" && value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d{1,6})?([+-]\d{2}:\d{2})$/);
    if(!m) return this.t("actionPanelLastInvalid");
    const year=Number(m[1]),month=Number(m[2]),day=Number(m[3]),leap=year%4===0&&(year%100!==0||year%400===0);
    const days=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
    if(year<1 || month<1 || month>12 || day<1 || day>days[month-1] || Number(m[4])>23 || Number(m[5])>59 || Number(m[6])>59 || Number(m[8].slice(1,3))>23 || Number(m[8].slice(4))>59) return this.t("actionPanelLastInvalid");
    return `${day} ${this.t("contextMonths")[month-1]} ${m[1]} · ${m[4]}:${m[5]}:${m[6]}${m[7]||""} · UTC${m[8]}`;
  }
  actionPanelPreviewMarkup(card) {
    if(!this.isActionPanelAction(card) && !this.isActionParametersAction(card)) return "";
    const meta=this.isActionParametersAction(card)?this.actionParametersMetadata(card):this.actionPanelMetadata(card);if(!meta)return "";
    const live=this._hass?.states?.[card.entity_id],domain=this.actionPanelDomain(card),momentary=["button","input_button","scene"].includes(domain);
    const source=live?.state==="unavailable"?"unavailable":typeof live?.state==="string" && (momentary || ["on","off"].includes(live.state))?"known":"unknown";
    const phase=source!=="known"?"unknown":momentary?"stateless":domain==="script"?(live.state==="on"?"running":"idle"):(live.state==="on"?"enabled":"disabled");
    const note=`<p class="hint">${this.t("extraPreviewNote")}</p>`;
    if(!live || source!==meta.state.source || phase!==meta.state.phase) return `<section data-action-panel-preview><p class="hint">${this.t("extraRefreshing")}</p>${note}</section>`;
    const state=meta.state,blocked=({needs_parameters:"actionPanelParameters",metadata_unavailable:"actionPanelMetadata",service_unavailable:"actionPanelRunService"})[meta.caps.run_blocked];
    const date=state.last_used_status==="value"?this.actionLastUsedText(state.last_used_text):this.t(state.last_used_status==="unknown"?"actionPanelLastUnknown":"actionPanelLastInvalid");
    return `<section data-action-panel-preview><p class="hint">${AEH_ESCAPE(date)}${state.current===null?"":`<br>${this.t("actionPanelCurrent")}: ${state.current}`}</p>${blocked?`<p class="hint">${this.t(blocked)}</p>`:""}${note}</section>`;
  }
  requestActionPanelPolicy(key,value) {
    const card=this.cardAt(this._selectedSlot);
    if(!this.validActionPanelAction(card) || this.actionPanelDomain(card)!=="automation" || !["skip_condition","stop_actions"].includes(key) || typeof value!=="boolean" || card.action[key]===value) return false;
    return this.requestLightControl("actionpanel",{...this.actionPanelPolicies(card),[key]:value});
  }
  isMediaPanelAction(card) {
    const a=card?.action;
    return card?.type==="entity" && card.entity_id?.startsWith("media_player.") && a?.kind==="control" &&
      a.control==="panel" && a.property==="media" && Object.keys(a).length===3;
  }
  validMediaPanelAction(card) {
    return this.isMediaPanelAction(card) && this.profile?.layout_versions?.includes(3) &&
      this.profile?.schema_control_types?.includes("panel") && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"media");
  }
  mediaPanelAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"mediaPanelUnsupported"},invalid={ready:false,reason:"mediaPanelEntity"};
    if (!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
      this._status?.device_available!==true || this._status.entity_control_status!=="ready" || !this._status.native_control_types?.includes("entity_control_v1") ||
      !this._status.control_kinds?.includes("panel") || !this.profile?.schema_control_types?.includes("panel") || !this.profile.layout_versions?.includes(3) ||
      !this.hasExtraProfile(this.profile.schema_panel_extra_profiles,"media") || !this.hasExtraProfile(this._status.panel_extra_profiles,"media")) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),live=this._hass?.states?.[card?.entity_id],meta=entity?.media_panel;
    const exact=(v,keys)=>v && typeof v==="object" && !Array.isArray(v) && Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k));
    const caps=meta?.caps,attrs=live?.attributes,features=attrs?.supported_features,services=this._hass?.services?.media_player;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || slot.slot<2 || !card.entity_id?.startsWith("media_player.") ||
      entity?.domain!=="media_player" || !live || !exact(meta,["version","caps","fingerprint","state","unsupported_facets"]) || meta.version!==1 ||
      typeof meta.fingerprint!=="string" || !/^[0-9a-f]{64}$/.test(meta.fingerprint) || !exact(caps,["device_type","operations","facets"]) ||
      !["generic","speaker","tv","receiver"].includes(caps.device_type) || !Number.isInteger(caps.operations) || caps.operations<0 || caps.operations>4095 ||
      !Number.isInteger(caps.facets) || caps.facets<0 || caps.facets>15 || !Number.isSafeInteger(features) || features<0 ||
      !services || typeof services!=="object" || Array.isArray(services)) return invalid;
    const definitions=[[16384,"media_play"],[1,"media_pause"],[16,"media_previous_track"],[32,"media_next_track"],[4096,"media_stop"],
      [128,"turn_on"],[256,"turn_off"],[4,"volume_set"],[4|1024,"volume_up"],[4|1024,"volume_down"],[8,"volume_mute"],[32768,"shuffle_set"]];
    const operations=definitions.reduce((mask,[flag,name],index)=>mask|((features&flag)&&Object.hasOwn(services,name)?1<<index:0),0);
    const validOptions=v=>Array.isArray(v) && v.length>=1 && v.length<=8 && new Set(v).size===v.length &&
      v.every(text=>typeof text==="string" && text.length>0 && !["unknown","unavailable"].includes(text) && new TextEncoder().encode(text).length<=32 &&
        [...text].every(c=>c===" " || !/[\p{C}\p{Z}]/u.test(c)));
    const catalogues={source:attrs.source_list,sound_mode:attrs.sound_mode_list,repeat:["off","one","all"]},choiceServices={source:[2048,"select_source",2],sound_mode:[65536,"select_sound_mode",4],repeat:[262144,"repeat_set",8]};
    let facets=(operations&128)?1:0;
    const admitted={};
    for (const [name,[flag,service,bit]] of Object.entries(choiceServices)) {
      if ((features&flag) && Object.hasOwn(services,service) && validOptions(catalogues[name])) { facets|=bit; admitted[name]=catalogues[name]; }
    }
    const deviceClass=["speaker","tv","receiver"].includes(attrs.device_class)?attrs.device_class:"generic";
    if (caps.operations!==operations || caps.facets!==facets || caps.device_type!==deviceClass) return invalid;
    // Capability identity excludes phase, volume, track title and position telemetry.
    return {ready:true,reason:"mediaPanelHint",caps:{capabilities:caps,fingerprint:meta.fingerprint,features,catalogues:admitted}};
  }
  isInfoContextCard(card) { return ["person","sun"].includes(card?.entity_id?.split(".")[0]); }
  hasInfoContextProfile(profiles,card) {
    return !this.isInfoContextCard(card) || this.hasExtraProfile(profiles,"info_context");
  }
  contextDateParts(text) {
    const m=typeof text==="string" && text.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-])(\d{2}):(\d{2})$/);
    if(!m) return null;
    const [y,month,day,hour,minute,second]=m.slice(1,7).map(Number),leap=y%4===0&&(y%100!==0||y%400===0);
    const days=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
    return y>=1 && month>=1 && month<=12 && day>=1 && day<=days[month-1] && hour<24 && minute<60 && second<60 && Number(m[8])<24 && Number(m[9])<60 ? m : null;
  }
  contextDateText(status,text) {
    if(status!=="value") return this.t(({unknown:"contextDateUnknown",invalid:"contextDateInvalid",stale:"contextDateStale",too_long:"extraTooLong"})[status]||"contextDateInvalid");
    const m=this.contextDateParts(text);
    if(!m) return this.t("contextDateInvalid");
    // Format the admitted local clock and offset, never the browser timezone.
    return `${Number(m[3])} ${this.t("contextMonths")[Number(m[2])-1]} ${m[1]} · ${m[4]}:${m[5]} · UTC${m[7]}${m[8]}:${m[9]}`;
  }
  contextAngleValid(text,negativeAllowed,maximum) {
    // Compare bounded decimal digits without rounding a just-outside value into range.
    const m=typeof text==="string" && text.match(/^([+-]?)(?:(\d+)(?:\.(\d*))?|\.(\d+))(?:[eE]([+-]?\d+))?$/);
    if(!m || text.length>24) return false;
    const fraction=m[3]??m[4]??"",digits=((m[2]??"")+fraction).replace(/^0+/,"");
    if(!digits) return true;
    if(m[1]==="-" && !negativeAllowed) return false;
    const scale=Number(m[5]||0)-fraction.length,limit=String(maximum),whole=digits.length+scale;
    if(whole!==limit.length) return whole<limit.length;
    const prefix=digits.padEnd(limit.length,"0").slice(0,limit.length);
    return prefix<limit || prefix===limit && !/[1-9]/.test(digits.slice(limit.length));
  }
  isExtraPanelAction(card) {
    const a=card?.action,family=this.extraPanelFamily(card);
    return !!family && a?.kind==="control" && a.control==="panel" && a.property===family && Object.keys(a).length===3 &&
      (card.type==="entity" || family==="info" && card.type==="sensor");
  }
  hasExtraProfile(profiles,family) {
    return Array.isArray(profiles) && profiles.length<=8 && new Set(profiles.map(p=>p?.name)).size===profiles.length &&
      profiles.every(p=>p && typeof p==="object" && !Array.isArray(p) && Object.keys(p).length===2 &&
        typeof p.name==="string" && /^[a-z][a-z0-9_]{0,23}$/.test(p.name) && Number.isInteger(p.version) && p.version>=1 && p.version<=255) &&
      profiles.some(p=>p.name===family && p.version===(family==="action"?2:1));
  }
  validExtraPanelAction(card) {
    if(this.isStatisticsAction(card)) return this.validStatisticsAction(card);
    if(this.isAgendaAction(card)) return this.validAgendaAction(card);
    return this.isExtraPanelAction(card) && this.profile?.layout_versions?.includes(3) &&
      this.profile?.schema_control_types?.includes("panel") && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,this.extraPanelFamily(card)) && this.hasInfoContextProfile(this.profile?.schema_panel_extra_profiles,card);
  }
  extraPanelMetadata(card) {
    const entity=this.entityFor(card?.entity_id),family=this.extraPanelFamily(card),domain=card?.entity_id?.split(".")[0],m=entity?.extra_panel;
    const exact=(v,keys)=>v && typeof v==="object" && !Array.isArray(v) && Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k));
    const text=(v,n)=>typeof v==="string" && new TextEncoder().encode(v).length<=n && !/[\p{C}\p{Zl}\p{Zp}]/u.test(v);
    if (!family || entity?.domain!==domain || !exact(m,["version","panel_type","caps","fingerprint","state","available","eligible_actions"]) ||
      m.version!==1 || m.panel_type!==family || typeof m.fingerprint!=="string" || !/^[0-9a-f]{64}$/.test(m.fingerprint)) return null;
    const c=m.caps,o=m.state,known=o?.source==="known",base=["source","updated_text"];
    if (!o || !["known","unknown","unavailable"].includes(o.source) || !text(o.updated_text,48) || m.available!==known ||
      !Number.isInteger(m.eligible_actions) || m.eligible_actions<0 || m.eligible_actions>(family==="lock"?1:0)) return null;
    const alarm=["disarmed","armed_home","armed_away","armed_night","armed_vacation","armed_custom_bypass","pending","arming","disarming","triggered","unknown"];
    if (family==="lock") {
      if (!exact(c,["lock"]) || typeof c.lock!=="boolean" || !exact(o,[...base,"phase"]) ||
        !["locked","unlocked","locking","unlocking","open","opening","jammed","unknown"].includes(o.phase) || !known && o.phase!=="unknown" ||
        m.eligible_actions!==(known && c.lock && ["unlocked","open","jammed"].includes(o.phase)?1:0)) return null;
    } else {
      const infoType=domain==="alarm_control_panel"?"alarm":domain;
      if (!exact(c,["info_type","device_class"]) || c.info_type!==infoType ||
        c.device_class!==null && (typeof c.device_class!=="string" || !/^[a-z][a-z0-9_]{0,31}$/.test(c.device_class)) ||
        ["calendar","alarm","person","sun"].includes(infoType) && c.device_class!==null) return null;
      if (["person","sun"].includes(infoType)) {
        const person=infoType==="person",dateKeys=person?["changed"]:["next_rising","next_setting"],angleKeys=person?[]:["elevation","azimuth"];
        const fields=[...base,"phase",...(person?["text_status","state_text"]:[]),...dateKeys.flatMap(k=>[k+"_status",k+"_text"]),...angleKeys.flatMap(k=>[k+"_status",k+"_text"]),"zone_text"];
        if(!exact(o,fields) || !text(o.zone_text,48) || o.updated_text && !this.contextDateParts(o.updated_text) ||
          !(person?["home","away","zone","unknown"]:["above_horizon","below_horizon","unknown"]).includes(o.phase)) return null;
        if(person && (!["value","empty","invalid","too_long","unknown"].includes(o.text_status) || !text(o.state_text,96) ||
          (o.text_status==="value")!==(o.state_text.length>0) || known && o.text_status==="unknown" ||
          known && o.phase==="unknown" && !["invalid","empty"].includes(o.text_status))) return null;
        for(const key of dateKeys) {
          const status=o[key+"_status"],value=o[key+"_text"];
          if(!["value","unknown","invalid","too_long",...(!person?["stale"]:[])].includes(status) || !text(value,40) ||
            (status==="value")!==(value.length>0) || status==="value" && (!o.zone_text || !this.contextDateParts(value))) return null;
        }
        for(const key of angleKeys) {
          const status=o[key+"_status"],value=o[key+"_text"];
          if(!["value","unknown","invalid","too_long"].includes(status) || !text(value,24) || (status==="value")!==(value.length>0) ||
            status==="value" && !this.contextAngleValid(value,key==="elevation",key==="elevation"?90:360)) return null;
        }
        if(!known && (o.phase!=="unknown" || o.zone_text!=="" || person && (o.text_status!=="unknown" || o.state_text!=="") ||
          [...dateKeys,...angleKeys].some(k=>o[k+"_status"]!=="unknown" || o[k+"_text"]!==""))) return null;
      } else if (infoType==="calendar") {
        const fields={summary:128,start_text:40,end_text:40,zone_text:48,location:96,description:64};
        if (!exact(o,[...base,"event","active",...Object.keys(fields),"all_day","truncated_fields"]) ||
          !["present","none","invalid","unknown"].includes(o.event) || !Number.isInteger(o.truncated_fields) || o.truncated_fields<0 || o.truncated_fields>7 ||
          Object.entries(fields).some(([k,n])=>!text(o[k],n))) return null;
        if (o.event==="present") {
          if (!known || typeof o.active!=="boolean" || typeof o.all_day!=="boolean" || !o.start_text || !o.end_text || !o.zone_text) return null;
        } else if (o.active!==null || o.all_day!==null || o.truncated_fields!==0 || Object.keys(fields).some(k=>o[k]!=="") ||
          known && o.event==="unknown" || !known && o.event!=="unknown") return null;
      } else {
        const sensor=infoType==="sensor",status=sensor?"value_status":"text_status",value=sensor?"value_text":"state_text",extra=sensor?"unit_text":infoType==="binary_sensor"?"active":"phase";
        if (!exact(o,[...base,status,value,extra]) || !["value","empty","invalid","too_long","unknown"].includes(o[status]) || !text(o[value],96) ||
          (o[status]==="value")!==(o[value].length>0) || !known && o[status]!=="unknown" || known && o[status]==="unknown") return null;
        if (sensor ? !text(o.unit_text,24) : infoType==="binary_sensor" ?
          (o.active!==null && typeof o.active!=="boolean" || !known && o.active!==null || known && o.active===null && o[status]!=="invalid") :
          (!alarm.includes(o.phase) || !known && o.phase!=="unknown" || known && o.phase==="unknown" && o[status]!=="invalid")) return null;
      }
    }
    return m;
  }
  extraPanelAvailability(card=this.cardAt(this._selectedSlot),family=this.extraPanelFamily(card)) {
    const unsupported={ready:false,reason:"extraUnsupported"},invalid={ready:false,reason:"extraEntity"};
    if (!family || family!==this.extraPanelFamily(card) || !this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
      this._status?.device_available!==true || this._status.entity_control_status!=="ready" || !this._status.native_control_types?.includes("entity_control_v1") ||
      !this._status.control_kinds?.includes("panel") || !this.profile?.schema_control_types?.includes("panel") || !this.profile.layout_versions?.includes(3) ||
      !this.hasExtraProfile(this.profile.schema_panel_extra_profiles,family) || !this.hasExtraProfile(this._status.panel_extra_profiles,family) || !this.hasInfoContextProfile(this.profile.schema_panel_extra_profiles,card) || !this.hasInfoContextProfile(this._status.panel_extra_profiles,card)) return unsupported;
    const place=this.slotAt(card?.slot),live=this._hass?.states?.[card?.entity_id],meta=this.extraPanelMetadata(card),entity=this.entityFor(card?.entity_id);
    if (!card || !["entity",...(family==="info"?["sensor"]:[])].includes(card.type) || !card.visible || !place?.editable || place.hidden || place.slot<2 || !live || !meta) return invalid;
    const service=Array.isArray(entity.actions) && entity.actions.some(a=>a?.service==="lock.lock");
    if (family==="lock" && meta.caps.lock && !service) return invalid;
    const raw=live.attributes?.device_class,observedClass=typeof raw==="string" && /^[a-z][a-z0-9_]{0,31}$/.test(raw)?raw:null;
    if (family==="info" && ["sensor","binary_sensor"].includes(meta.caps.info_type) && meta.caps.device_class!==observedClass) return invalid;
    // Review capability identity only: normal observations, outages and time updates do not rewrite a passive launcher.
    return {ready:true,reason:family==="info"?"extraInfoHint":meta.caps.lock?"extraLockHint":"extraLockPassive",
      caps:{family,capabilities:meta.caps,fingerprint:meta.fingerprint,observedClass:family==="info" && !this.isInfoContextCard(card)?observedClass:null,lockService:family==="lock"?service:null}};
  }
  extraLockStateText(card,observation) {
    const phase=observation.phase,live=this._hass?.states?.[card.entity_id];
    if (phase==="unknown") return this.t("unknown");
    // Translate the admitted observation, not a different live phase.
    if (live?.state===phase && typeof this._hass.formatEntityState==="function") {
      try {
        const text=this._hass.formatEntityState(live);
        if (typeof text==="string" && text.trim() && text!==phase && new TextEncoder().encode(text).length<=96 &&
            !/[\p{C}\p{Zl}\p{Zp}]/u.test(text)) return text;
      } catch { /* The local language pack covers older or unloaded HA resources. */ }
    }
    return this.t(({locked:"extraLockLocked",unlocked:"extraLockUnlocked",locking:"extraLockLocking",unlocking:"extraLockUnlocking",
      open:"extraLockOpen",opening:"extraLockOpening",jammed:"extraLockJammed"})[phase] || "unknown");
  }
  extraPreview(card) {
    const meta=this.extraPanelMetadata(card),live=this._hass?.states?.[card?.entity_id];
    if (this._hass?.connected===false || !live || live.state==="unavailable") return {message:this.t("offline")};
    if (live.state==="unknown") return {message:this.t("unknown")};
    if (!meta) {
      if (this.extraPanelAvailability(card).reason==="extraUnsupported") return {message:this.t("extraUnsupported")};
      const read=this._entityMetadataReads.get(card?.entity_id);
      const current=read?.state===live;
      const reason=this.entityFor(card?.entity_id) || current && read?.status==="loaded" ? "extraEntity" : current && read?.status==="failed" ? "extraLoadFailed" : "extraLoading";
      return {message:this.t(reason)};
    }
    const o=meta.state;
    if (o.source!=="known") return {message:this.t(o.source==="unavailable"?"offline":"unknown")};
    // Do not expose an old catalogue value as the current value after a hass update.
    if (live.last_updated && (!o.updated_text || !Number.isFinite(Date.parse(live.last_updated)) ||
      Math.floor(Date.parse(live.last_updated)/1000)!==Math.floor(Date.parse(o.updated_text)/1000))) return {message:this.t("extraRefreshing")};
    if(this.isInfoContextCard(card)) {
      const catalogueState=this.entityFor(card.entity_id)?.state;
      if(typeof catalogueState==="string" && catalogueState!==live.state) return {message:this.t("extraRefreshing")};
      const person=meta.caps.info_type==="person",raw=live.state;
      const phase=person?(raw==="home"?"home":raw==="not_home"?"away":typeof raw==="string" && raw.trim()?"zone":"unknown"):
        ["above_horizon","below_horizon"].includes(raw)?raw:"unknown";
      if(phase!==o.phase) return {message:this.t("extraRefreshing")};
      const message=person?(o.text_status==="value"?o.state_text:this.t(({too_long:"extraTooLong",invalid:"extraInvalid",empty:"extraEmpty",unknown:"unknown"})[o.text_status])):
        this.t(({above_horizon:"contextAbove",below_horizon:"contextBelow"})[o.phase]||"unknown");
      return {meta,observation:o,message};
    }
    const status=o.value_status??o.text_status;
    if (status && status!=="value") return {message:this.t(({too_long:"extraTooLong",invalid:"extraInvalid",empty:"extraEmpty",unknown:"unknown"})[status])};
    if (meta.caps.info_type==="calendar" && o.event!=="present") return {message:this.t(o.event==="none"?"extraNoEvent":"extraInvalid")};
    return {meta,observation:o,message:meta.panel_type==="lock"?this.extraLockStateText(card,o):meta.caps.info_type==="calendar"?o.summary:(o.value_text??o.state_text)+(o.unit_text?" "+o.unit_text:"")};
  }
  extraPanelIcon(card) {
    const meta=this.extraPanelMetadata(card),type=meta?.caps.info_type,cls=meta?.caps.device_class;
    if (meta?.panel_type==="lock") return "mdi:lock-outline";
    if (type==="person") return "mdi:account";
    if (type==="sun") return "mdi:white-balance-sunny";
    if (type==="calendar") return "mdi:calendar-blank-outline";
    if (type==="alarm") return "mdi:shield-home-outline";
    return ({moisture:"mdi:water-alert-outline",humidity:"mdi:water-percent",temperature:"mdi:thermometer",door:"mdi:door",window:"mdi:window-closed",motion:"mdi:motion-sensor",occupancy:"mdi:account"})[cls] || "mdi:information-outline";
  }
  extraPanelPreviewMarkup(card) {
    if (!this.isExtraPanelAction(card)) return "";
    const p=this.extraPreview(card),o=p.observation;
    const line=(label,value)=>`<p><strong>${this.t(label)}</strong> ${AEH_ESCAPE(value)}</p>`;
    const excerpt=bit=>o.truncated_fields&bit?` <span class="hint">(${this.t("extraExcerpt")})</span>`:"";
    let content=`<p>${AEH_ESCAPE(p.message)}</p>`;
    if (o && p.meta.caps.info_type==="calendar") content=`<p>${AEH_ESCAPE(o.summary)}${excerpt(1)}</p>`+
      line("extraStart",o.start_text)+line("extraEnd",o.end_text)+line("extraZone",o.zone_text)+(o.all_day?`<p>${this.t("extraAllDay")}</p>`:"")+
      (o.location?`<p><strong>${this.t("extraLocation")}</strong> ${AEH_ESCAPE(o.location)}${excerpt(2)}</p>`:"")+
      (o.description?`<p><strong>${this.t("extraDescription")}</strong> ${AEH_ESCAPE(o.description)}${excerpt(4)}</p>`:"");
    if(o && this.isInfoContextCard(card)) {
      if(p.meta.caps.info_type==="person") content+=line("contextChanged",this.contextDateText(o.changed_status,o.changed_text));
      else {
        for(const [key,label] of [["next_rising","contextRise"],["next_setting","contextSet"]]) content+=line(label,this.contextDateText(o[key+"_status"],o[key+"_text"]));
        for(const [key,label] of [["elevation","contextElevation"],["azimuth","contextAzimuth"]]) {
          const value=o[key+"_status"]==="value"?o[key+"_text"].replace(".",this.carouselText(",","."))+"°":
            this.t(({unknown:"unknown",invalid:"extraInvalid",too_long:"extraTooLong"})[o[key+"_status"]]);
          content+=line(label,value);
        }
      }
      if(o.zone_text) content+=line("extraZone",o.zone_text);
    }
    return `<section data-extra-panel-preview style="overflow-wrap:anywhere;white-space:normal">${this.icon(this.extraPanelIcon(card))}<h3>${this.t("extraPreview")}</h3>${content}`+
      (o?.updated_text?line("extraUpdated",this.isInfoContextCard(card)?this.contextDateText("value",o.updated_text):o.updated_text):"")+`<p class="hint">${this.t("extraPreviewNote")}</p></section>`;
  }
  sensorActionEditable(card) {
    return card?.type!=="sensor" || this.isStatisticsAction(card) || this.statisticsAvailability(card).ready || this.isAgendaAction(card) || this.agendaAvailability(card).ready || this.textPanelAvailability(card).ready || this.datetimePanelAvailability(card).ready || this.isExtraPanelAction(card) || this.extraPanelAvailability(card,"info").ready;
  }
  panelFamily(card) {
    return ({timer:"timer",remote:"remote",switch:"power",input_boolean:"power"})[card?.entity_id?.split(".")[0]] || null;
  }
  validPanelAction(card) {
    const action=card?.action,family=this.panelFamily(card);
    return !!family && action?.kind==="control" && action.control==="panel" && action.property===family &&
      this.profile?.schema_panel_control===true && this.profile.schema_control_types?.includes("panel") &&
      this.profile.schema_panel_types?.includes(family) && Object.keys(action).every(k=>["kind","control","property","initial_duration"].includes(k)) &&
      (!Object.hasOwn(action,"initial_duration") || family==="timer" && Number.isInteger(action.initial_duration) && action.initial_duration>=1 && action.initial_duration<=86400);
  }
  panelControlAvailability(card=this.cardAt(this._selectedSlot),family=this.panelFamily(card)) {
    const unsupported={ready:false,reason:"panelUnsupported"},unavailable={ready:false,reason:"panelEntity"};
    if (!family || family!==this.panelFamily(card) || !this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
        this._status?.device_available!==true || this._status.entity_control_status!=="ready" || this._status.panel_version!==1 ||
        !this._status.panel_types?.includes(family) || !this._status.native_control_types?.includes("entity_control_v1") ||
        !this._status.control_kinds?.includes("panel") || this.profile?.schema_panel_control!==true ||
        !this.profile.schema_control_types?.includes("panel") || !this.profile.schema_panel_types?.includes(family) || !this.profile.layout_versions?.includes(3)) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id],domain=card?.entity_id?.split(".")[0];
    const meta=entity?.panel_control,caps=meta?.caps;
    const exact=(value,keys)=>!!value && typeof value==="object" && !Array.isArray(value) && Object.keys(value).length===keys.length && keys.every(k=>Object.hasOwn(value,k));
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || slot.slot<2 ||
        entity?.domain!==domain || entity.available!==true || meta?.version!==1 || meta.panel_type!==family || meta.available!==true ||
        !state || !caps || !meta.state || !Number.isInteger(meta.eligible_actions) || meta.eligible_actions<0) return unavailable;
    const services=Array.isArray(entity.actions)?entity.actions.map(a=>a?.service):[];
    const has=op=>services.includes(`${domain}.${op}`),bools=keys=>keys.every(k=>typeof caps[k]==="boolean");
    if (family==="timer") {
      if (!exact(caps,["start","pause","cancel","initial_duration"]) || !bools(["start","pause","cancel"]) || caps.initial_duration!==null ||
          !["idle","active","paused"].includes(state.state) || meta.eligible_actions>31 ||
          !["start","pause","cancel"].some(k=>caps[k]) || ["start","pause","cancel"].some(k=>caps[k] && !has(k))) return unavailable;
    } else {
      const keys=family==="remote"?["turn_on","turn_off","activities"]:["turn_on","turn_off","device_class"];
      if (!exact(caps,keys) || !bools(["turn_on","turn_off"]) || !["on","off"].includes(state.state) ||
          !(caps.turn_on || caps.turn_off) || caps.turn_on && !has("turn_on") || caps.turn_off && !has("turn_off") || meta.eligible_actions>(family==="remote"?7:3)) return unavailable;
      if (family==="power" && !["outlet","switch","unknown"].includes(caps.device_class)) return unavailable;
      if (family==="remote") {
        const values=caps.activities,features=state.attributes?.supported_features;
        if (!Array.isArray(values) || values.length>8 || new Set(values).size!==values.length ||
            values.some(v=>typeof v!=="string" || !v.trim() || new TextEncoder().encode(v).length>32 || /[\x00-\x1f\x7f]/.test(v) || ["unknown","unavailable"].includes(v)) ||
            values.length && (!Number.isSafeInteger(features) || features<0 || !(features&4) || !caps.turn_on ||
              JSON.stringify(values)!==JSON.stringify(state.attributes?.activity_list))) return unavailable;
      }
    }
    // A review follows capabilities, not per-second Timer observations.
    return {ready:true,reason:family+"PanelHint",caps:{family,capabilities:caps,
      ...(family==="remote"?{features:state.attributes?.supported_features,activities:state.attributes?.activity_list}:{}),
      ...(family==="power"?{deviceClass:state.attributes?.device_class}:{} )}};
  }
  robotPanelAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"robotUnsupported"},unavailable={ready:false,reason:"robotEntity"};
    if (!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
        this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
        this._status.robot_control_supported!==true || !this._status.native_control_types?.includes("entity_control_v1") ||
        !this._status.control_kinds?.includes("robot") || this.profile?.schema_robot_control!==true ||
        !this.profile.layout_versions?.includes(3) || !this.profile.schema_control_types?.includes("robot")) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id];
    const meta=entity?.robot_control,caps=meta?.caps,domain=card?.entity_id?.split(".")[0],features=state?.attributes?.supported_features;
    const mower=domain==="lawn_mower",activities=mower?["mowing","docked","paused","returning","error"]:["cleaning","docked","idle","paused","returning","error"];
    const names=values=>Array.isArray(values) && values.length<=8 && new Set(values).size===values.length &&
      values.every(v=>typeof v==="string" && v.length>0 && new TextEncoder().encode(v).length<=32 && !/[\x00-\x1f\x7f]/.test(v));
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden ||
        !["vacuum","lawn_mower"].includes(domain) || entity?.domain!==domain || entity.available!==true ||
        !activities.includes(state?.state) || meta?.version!==1 || meta.robot_type!==domain ||
        !/^[0-9a-f]{64}$/.test(meta.catalogue_fingerprint) || !caps || Object.keys(caps).length!==3 ||
        !Number.isInteger(caps.actions) || caps.actions<0 || caps.actions>63 || mower && (caps.actions & ~11)!==0 ||
        !names(caps.speeds) || !names(caps.areas) || mower && (caps.speeds.length || caps.areas.length) ||
        !(caps.actions || caps.speeds.length || caps.areas.length) ||
        ![null,"unsupported","no_mapped_areas","too_many_areas","area_labels_unsupported"].includes(meta.area_reason) ||
        !Number.isSafeInteger(features) || features<0 || features>2147483647) return unavailable;
    const actions=Array.isArray(entity.actions)?entity.actions:[];
    const required=mower?{1:[1,"start_mowing"],2:[2,"pause"],8:[4,"dock"]}:
      {1:[8192,"start"],2:[4,"pause"],4:[8,"stop"],8:[16,"return_to_base"],16:[512,"locate"],32:[1024,"clean_spot"]};
    if (Object.entries(required).some(([bit,[feature,service]])=>(caps.actions & Number(bit)) &&
        (!(features & feature) || !actions.some(action=>action?.service===`${domain}.${service}`))) ||
        caps.speeds.length && (!(features & 32) || !actions.some(action=>action?.service==="vacuum.set_fan_speed")) ||
        caps.areas.length && (!(features & 16384) || !actions.some(action=>action?.service==="vacuum.clean_area"))) return unavailable;
    const areaHints={unsupported:"robotAreaUnsupported",no_mapped_areas:"robotAreaUnmapped",too_many_areas:"robotAreaTooMany",area_labels_unsupported:"robotAreaLabels"};
    return {ready:true,reason:mower?"robotMowerHint":areaHints[meta.area_reason] || "robotHint",caps:{type:domain,capabilities:caps,fingerprint:meta.catalogue_fingerprint,
      features,speeds:state.attributes?.fan_speed_list}};
  }
  fanControlAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"fanUnsupported"};
    if (!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
        this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
        !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("fan") ||
        !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("fan")) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id],caps=entity?.fan_control?.caps;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="fan" ||
        !card.entity_id.startsWith("fan.") || entity.available!==true || !["on","off"].includes(state?.state) || !caps ||
        !["turn_on","turn_off","oscillate","direction"].every(key=>typeof caps[key]==="boolean") ||
        !Array.isArray(caps.speeds) || caps.speeds.length>8 || !caps.speeds.every(v=>Number.isInteger(v) && v>=0 && v<=100) ||
        !Array.isArray(caps.presets) || caps.presets.length>8 || !caps.presets.every(v=>typeof v==="string" && new TextEncoder().encode(v).length<=32)) return {ready:false,reason:"fanEntity"};
    const services=entity.actions?.map(action=>action.service) || [];
    if ((caps.turn_on && !services.includes("fan.turn_on")) || (caps.turn_off && !services.includes("fan.turn_off")) ||
        (caps.oscillate && !services.includes("fan.oscillate")) || (caps.direction && !services.includes("fan.set_direction")) ||
        (caps.speeds.length && !services.includes("fan.set_percentage")) || (caps.presets.length && !services.includes("fan.set_preset_mode"))) return {ready:false,reason:"fanEntity"};
    return {ready:true,reason:"fanHint",caps:{...caps,features:state.attributes?.supported_features,speedCount:state.attributes?.percentage_step,presetModes:state.attributes?.preset_modes}};
  }
  humidityPanelAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"humidityPanelUnsupported"};
    if (!this.isConnected || this._statusError || this._profileStale || this._hass?.connected===false ||
        this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
        !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("humidifier") ||
        !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("humidifier")) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id];
    const meta=entity?.humidifier_control,caps=meta?.caps,domain=meta?.humidity_domain,attrs=state?.attributes;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="humidifier" ||
        !card.entity_id.startsWith("humidifier.") || entity.available!==true || !["on","off"].includes(state?.state) || !caps ||
        typeof caps.turn_on!=="boolean" || typeof caps.turn_off!=="boolean" ||
        !Array.isArray(caps.modes) || caps.modes.length>8 || new Set(caps.modes).size!==caps.modes.length ||
        !caps.modes.every(v=>typeof v==="string" && v.length>0 && new TextEncoder().encode(v).length<=32) ||
        !["humidifier","dehumidifier","unknown"].includes(meta.device_class) ||
        !(domain===null || domain?.schema==="numeric_steps_v1" && domain.unit==="%" &&
          Number.isInteger(domain.max_index) && domain.max_index>=0 && domain.max_index<=100)) return {ready:false,reason:"humidityPanelEntity"};
    const services=entity.actions?.map(action=>action.service) || [];
    if ((caps.turn_on && !services.includes("humidifier.turn_on")) || (caps.turn_off && !services.includes("humidifier.turn_off")) ||
        (domain && !services.includes("humidifier.set_humidity")) || (caps.modes.length && !services.includes("humidifier.set_mode")) ||
        !(caps.turn_on || caps.turn_off || domain || caps.modes.length)) return {ready:false,reason:"humidityPanelEntity"};
    return {ready:true,reason:"humidityPanelHint",caps:{caps,domain,deviceClass:meta.device_class,attributes:{
      features:attrs?.supported_features,min:attrs?.min_humidity,max:attrs?.max_humidity,step:attrs?.target_humidity_step,
      modes:attrs?.available_modes,deviceClass:attrs?.device_class}}};
  }
  controlAvailability(card,kind="light") {
    if(kind==="statisticspanel") return this.statisticsAvailability(card);
    if(kind==="agendapanel") return this.agendaAvailability(card);
    if (kind==="textpanel") return this.textPanelAvailability(card);
    if (kind==="datetimepanel") return this.datetimePanelAvailability(card);
    if (kind==="actionparameterspanel") return this.actionParametersAvailability(card);
    if (kind==="actionpanel") return this.actionPanelAvailability(card);
    if (kind==="mediapanel") return this.mediaPanelAvailability(card);
    if (["infopanel","lockpanel"].includes(kind)) return this.extraPanelAvailability(card,kind.slice(0,-5));
    if (kind==="lightdetail" || kind==="climatepanel") return this.detailControlAvailability(card,kind==="lightdetail"?"light":"climate");
    if (["timerpanel","remotepanel","powerpanel"].includes(kind)) return this.panelControlAvailability(card,kind.slice(0,-5));
    if (kind === "robot") return this.robotPanelAvailability(card);
    if (kind === "humiditypanel") return this.humidityPanelAvailability(card);
    if (kind === "fan") return this.fanControlAvailability(card);
    if (kind === "direction") return this.fanDirectionAvailability(card);
    if (kind === "covertilt") return this.coverTiltAvailability(card);
    if (kind === "coverposition") return this.coverPositionAvailability(card);
    if (kind === "mediarepeat") return this.mediaRepeatAvailability(card);
    if (kind === "mediasound") return this.mediaSoundAvailability(card);
    if (kind === "mediasource") return this.mediaSourceAvailability(card);
    if (kind === "remoteactivity") return this.remoteActivityAvailability(card);
    if (kind === "vacuumfan") return this.vacuumPowerAvailability(card);
    if (kind === "speed") return this.fanSpeedAvailability(card);
    if (kind === "kelvin") return this.lightColorTemperatureAvailability(card);
    if (kind === "climatehumidity") return this.climateHumidityAvailability(card);
    if (kind === "humidity") return this.humidifierHumidityAvailability(card);
    if (kind === "temperature") return this.climateTemperatureAvailability(card);
    if (kind === "hvac") return this.climateHVACAvailability(card);
    if (kind === "preset") return this.climatePresetAvailability(card);
    if (kind === "airflow") return this.climateFanAvailability(card);
    if (kind === "swing") return this.climateSwingAvailability(card);
    if (kind === "horizontal") return this.climateHorizontalAvailability(card);
    if (kind === "effect") return this.lightEffectAvailability(card);
    if (kind === "humidifier") return this.humidifierModeAvailability(card);
    return kind === "number" ? this.numberControlAvailability(card) : kind === "choice" ? this.choiceControlAvailability(card) : kind === "cover" ? this.coverControlAvailability(card) : this.lightControlAvailability(card);
  }
  cardControlKind(card) {
    if(this.isActionParametersAction(card)) return "actionparameterspanel";
    if(this.isStatisticsAction(card)) return "statisticspanel";
    if(this.isAgendaAction(card)) return "agendapanel";
    if(this.isTextPanelAction(card) || card?.entity_id?.startsWith("input_text.") && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"text")) return "textpanel";
    if (this.isDatetimePanelAction(card) || this.isDatetimeCard(card) && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"datetime")) return "datetimepanel";
    if (this.isActionPanelAction(card) || this.actionPanelDomain(card) && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"action")) return "actionpanel";
    if (this.isMediaPanelAction(card)) return "mediapanel";
    if (this.extraPanelFamily(card)) return this.extraPanelFamily(card)+"panel";
    if (card?.entity_id?.startsWith("light.") && card.action?.detail===1) return "lightdetail";
    if (card?.entity_id?.startsWith("climate.") && (card.action?.control==="panel" && card.action.property==="climate" || this.profile?.schema_climate_panel===true && this._status?.climate_panel_version===1)) return "climatepanel";
    if (this.panelFamily(card) && (card.action?.control==="panel" || this.profile?.schema_panel_control===true && this._status?.panel_types?.includes(this.panelFamily(card)))) return this.panelFamily(card)+"panel";
    if(["vacuum","lawn_mower"].includes(card?.entity_id?.split(".")[0])) return "robot";
    if(card?.entity_id?.startsWith("humidifier.")) return "humiditypanel";
    if(card?.entity_id?.startsWith("fan.")) return "fan";
    if(card?.entity_id?.startsWith("media_player.") && card.action?.property==="repeat") return "mediarepeat";
    if(card?.entity_id?.startsWith("media_player.") && card.action?.property==="sound_mode") return "mediasound";
    if(card?.entity_id?.startsWith("media_player.") && card.action?.property==="source") return "mediasource";
    if(card?.entity_id?.startsWith("remote.") && card.action?.property==="activity") return "remoteactivity";
    if(card?.entity_id?.startsWith("media_player.") && this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,"media")) return "mediapanel";
    return this.isNumberEntity(card) ? "number" : this.isChoiceEntity(card) ? "choice" : card?.entity_id?.startsWith("cover.") ? "cover" : "light";
  }
  coverPanelAvailability(card) {
    const unavailable={ready:false,reason:"coverPanelEntity"};
    if (this.profile?.schema_cover_panel!==true) return {ready:false,reason:"coverUnsupported"};
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id];
    const meta=entity?.cover_panel,caps=meta?.caps,features=state?.attributes?.supported_features;
    const operations={open:[1,"open_cover"],close:[2,"close_cover"],set_position:[4,"set_cover_position"],stop:[8,"stop_cover"],
      open_tilt:[16,"open_cover_tilt"],close_tilt:[32,"close_cover_tilt"],stop_tilt:[64,"stop_cover_tilt"],set_tilt_position:[128,"set_cover_tilt_position"]};
    const classes=["awning","blind","curtain","damper","door","garage","gate","shade","shutter","window","unknown"];
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden ||
        !card.entity_id.startsWith("cover.") || entity?.domain!=="cover" || entity.available!==true ||
        !["open","opening","closed","closing"].includes(state?.state) || meta?.version!==1 || !classes.includes(meta?.device_class) ||
        !caps || Array.isArray(caps) || Object.keys(caps).length!==8 || !Object.keys(caps).every(key=>Object.hasOwn(operations,key)) ||
        !Object.values(caps).every(value=>typeof value==="boolean") || !Object.values(caps).some(Boolean) ||
        !Number.isSafeInteger(features) || features<0 || features>2147483647) return unavailable;
    const actions=Array.isArray(entity.actions)?entity.actions:[];
    if (Object.entries(caps).some(([operation,supported])=>supported && (!(features & operations[operation][0]) ||
        !actions.some(action=>action?.service===`cover.${operations[operation][1]}`)))) return unavailable;
    return {ready:true,reason:"coverPanelHint",caps:{version:1,operations:caps,deviceClass:meta.device_class,
      features,sourceClass:state.attributes?.device_class}};
  }
  coverControlAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported = {ready:false,reason:"coverUnsupported"};
    if (!this.isConnected || this._statusError || this._profileStale || this._status.device_available !== true || this._status.entity_control_status !== "ready" || this._status.cover_stop_version !== 1 ||
        !Array.isArray(this._status.native_control_types) || !this._status.native_control_types.includes("entity_control_v1") ||
        !Array.isArray(this._status.control_kinds) || !this._status.control_kinds.includes("cover") ||
        !Array.isArray(this.profile?.layout_versions) || !this.profile.layout_versions.includes(3) ||
        !Array.isArray(this.profile?.schema_control_types) || !this.profile.schema_control_types.includes("cover")) return unsupported;
    if (this._status.cover_panel_version===1) return this.coverPanelAvailability(card);
    const slot = this.slotAt(card?.slot), entity = this.entityFor(card?.entity_id), state = this._hass?.states?.[card?.entity_id];
    const caps = entity?.cover_control?.caps, actions = Array.isArray(entity?.actions) ? entity.actions : [], features = state?.attributes?.supported_features;
    const bits = {open:1,stop:8,close:2};
    if (!card || card.type !== "entity" || !card.visible || !slot?.editable || slot.hidden || !card.entity_id.startsWith("cover.") || entity?.domain !== "cover" || entity.available !== true ||
        !state || !["open","opening","closed","closing"].includes(state.state) || !caps || typeof caps !== "object" || Array.isArray(caps) ||
        Object.keys(caps).length !== 3 || !Object.keys(caps).every(key=>Object.hasOwn(bits,key)) ||
        !Object.values(caps).every(value=>typeof value === "boolean") || !Object.values(caps).some(Boolean) ||
        !Number.isSafeInteger(features) || features < 0 || features > 2147483647 ||
        Object.entries(caps).some(([operation,enabled])=>enabled && (!(features & bits[operation]) || !actions.some(action=>action?.service === `cover.${operation}_cover`)))) return {ready:false,reason:"coverEntity"};
    return {ready:true,reason:"coverHint",caps:{operations:caps}};
  }
  isChoiceEntity(card) { return ["select","input_select","fan"].includes(card?.entity_id?.split(".")[0]); }
  observedClimatePreset(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.climate_preset_mode,options=meta?.options,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("climate.") || !["off","heat","cool","heat_cool","auto","dry","fan_only"].includes(state?.state) ||
      !Number.isSafeInteger(features) || features<0 || !(features & 16) || !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs?.preset_modes) || !Object.hasOwn(attrs,"preset_mode")) return null;
    const index=options.indexOf(attrs.preset_mode),empty=attrs.preset_mode===null || (attrs.preset_mode==="none" && index<0);
    return index>=0 || empty ? {options:[...options],index:index>=0?index:null,empty} : null;
  }
  climatePresetAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"presetUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_climate_preset_mode!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedClimatePreset(card);
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="climate" || entity.available!==true || !observed ||
      observed.empty && this._status.empty_choice_version!==1 || !entity.actions?.some(action=>action?.service==="climate.set_preset_mode")) return {ready:false,reason:"presetEntity"};
    return {ready:true,reason:"presetHint",caps:{options:observed.options}};
  }
  observedClimateFan(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.climate_fan_mode,options=meta?.options,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("climate.") || !["off","heat","cool","heat_cool","auto","dry","fan_only"].includes(state?.state) ||
      !Number.isSafeInteger(features) || features<0 || !(features & 8) || !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs?.fan_modes) || !Object.hasOwn(attrs,"fan_mode")) return null;
    const index=options.indexOf(attrs.fan_mode);
    return index>=0 ? {options:[...options],index} : null;
  }
  climateFanAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"airflowUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_climate_fan_mode!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedClimateFan(card);
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="climate" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action?.service==="climate.set_fan_mode")) return {ready:false,reason:"airflowEntity"};
    return {ready:true,reason:"airflowHint",caps:{options:observed.options}};
  }
  observedClimateSwing(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.climate_swing_mode,options=meta?.options,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("climate.") || !["off","heat","cool","heat_cool","auto","dry","fan_only"].includes(state?.state) ||
      !Number.isSafeInteger(features) || features<0 || !(features & 32) || !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs?.swing_modes) || !Object.hasOwn(attrs,"swing_mode")) return null;
    const index=options.indexOf(attrs.swing_mode);
    return index>=0 ? {options:[...options],index} : null;
  }
  climateSwingAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"swingUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_climate_swing_mode!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedClimateSwing(card);
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="climate" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action?.service==="climate.set_swing_mode")) return {ready:false,reason:"swingEntity"};
    return {ready:true,reason:"swingHint",caps:{options:observed.options}};
  }
  observedClimateHorizontal(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.climate_swing_horizontal_mode,options=meta?.options,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("climate.") || !["off","heat","cool","heat_cool","auto","dry","fan_only"].includes(state?.state) ||
      !Number.isSafeInteger(features) || features<0 || !(features & 512) || !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs?.swing_horizontal_modes) || !Object.hasOwn(attrs,"swing_horizontal_mode")) return null;
    const index=options.indexOf(attrs.swing_horizontal_mode);
    return index>=0 ? {options:[...options],index} : null;
  }
  climateHorizontalAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"horizontalUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_climate_swing_horizontal_mode!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedClimateHorizontal(card);
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="climate" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action?.service==="climate.set_swing_horizontal_mode")) return {ready:false,reason:"horizontalEntity"};
    return {ready:true,reason:"horizontalHint",caps:{options:observed.options}};
  }
  observedLightEffect(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.light_effect,options=meta?.options,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("light.") || !["on","off"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 4) ||
      !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs?.effect_list) || !Object.hasOwn(attrs,"effect") || state.state==="off" && attrs.effect!==null) return null;
    const index=options.indexOf(attrs.effect),empty=attrs.effect===null;
    return index>=0 || empty ? {options:[...options],index:index>=0?index:null,empty} : null;
  }
  lightEffectAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"effectUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_light_effect!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedLightEffect(card);
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="light" || entity.available!==true || !observed ||
      observed.empty && this._status.empty_choice_version!==1 || !entity.actions?.some(action=>action?.service==="light.turn_on" && Array.isArray(action.fields?.effect?.options) && JSON.stringify(action.fields.effect.options)===JSON.stringify(observed.options))) return {ready:false,reason:"effectEntity"};
    return {ready:true,reason:"effectHint",caps:{options:observed.options,empty:observed.empty}};
  }
  observedRemoteActivity(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.remote_activity,options=meta?.options,features=attrs?.supported_features;
    if(!card?.entity_id?.startsWith("remote.") || !["on","off"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 4) ||
      !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs.activity_list)) return null;
    const empty=state.state==="off",index=empty?-1:options.indexOf(attrs.current_activity);
    if(!empty && index<0 || meta.index!==(empty?null:index) || (meta.empty===true)!==empty) return null;
    return {options:[...options],index,empty};
  }
  remoteActivityAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"activityUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if(!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_remote_activity!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedRemoteActivity(card);
    if(!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="remote" || entity.available!==true || !observed ||
      observed.empty && this._status.empty_choice_version!==1 || !entity.actions?.some(action=>action.service==="remote.turn_on")) return {ready:false,reason:"activityEntity"};
    return {ready:true,reason:"activityHint",caps:observed};
  }
  observedMediaSource(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.media_source,options=meta?.options,features=attrs?.supported_features;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","idle","playing","paused","buffering"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 2048) ||
      !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs.source_list)) return null;
    const index=options.indexOf(attrs.source);
    if(index<0 || meta.index!==index || meta.empty===true) return null;
    return {options:[...options],index};
  }
  mediaSourceAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"mediaSourceUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if(!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_media_source!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedMediaSource(card);
    if(!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="media_player" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action.service==="media_player.select_source" && action.fields?.source?.required===true && action.fields.source.type==="select" && JSON.stringify(action.fields.source.options)===JSON.stringify(observed.options))) return {ready:false,reason:"mediaSourceEntity"};
    return {ready:true,reason:"mediaSourceHint",caps:observed};
  }
  observedMediaSound(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.media_sound_mode,options=meta?.options,features=attrs?.supported_features;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","idle","playing","paused","buffering"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 65536) ||
      !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs.sound_mode_list)) return null;
    const index=options.indexOf(attrs.sound_mode);
    if(index<0 || meta.index!==index || meta.empty===true) return null;
    return {options:[...options],index};
  }
  mediaSoundAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"mediaSoundUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if(!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_media_sound_mode!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedMediaSound(card);
    if(!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="media_player" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action.service==="media_player.select_sound_mode" && action.fields?.sound_mode?.required===true && action.fields.sound_mode.type==="select" && JSON.stringify(action.fields.sound_mode.options)===JSON.stringify(observed.options))) return {ready:false,reason:"mediaSoundEntity"};
    return {ready:true,reason:"mediaSoundHint",caps:observed};
  }
  observedMediaRepeat(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.media_repeat,options=meta?.options,features=attrs?.supported_features;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","idle","playing","paused","buffering"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 262144) ||
      !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(["off","one","all"])) return null;
    const index=options.indexOf(attrs.repeat);
    if(index<0 || meta.index!==index || meta.empty===true) return null;
    return {options:[...options],index};
  }
  mediaRepeatAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"mediaRepeatUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if(!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_media_repeat!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status.native_control_types?.includes("entity_control_v1") || !this._status.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedMediaRepeat(card);
    if(!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="media_player" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action.service==="media_player.repeat_set" && action.fields?.repeat?.required===true && action.fields.repeat.type==="select" && JSON.stringify(action.fields.repeat.options)===JSON.stringify(observed.options))) return {ready:false,reason:"mediaRepeatEntity"};
    return {ready:true,reason:"mediaRepeatHint",caps:observed};
  }
  observedHumidifierMode(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.humidifier_mode,options=meta?.options,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("humidifier.") || !["on","off"].includes(state?.state) ||
      !Number.isSafeInteger(features) || features<0 || !(features & 1) || !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs?.available_modes) || !Object.hasOwn(attrs,"mode")) return null;
    const index=options.indexOf(attrs.mode);
    return index>=0 ? {options:[...options],index} : null;
  }
  humidifierModeAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"humiModeUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_humidifier_mode!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedHumidifierMode(card);
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="humidifier" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action?.service==="humidifier.set_mode")) return {ready:false,reason:"humiModeEntity"};
    return {ready:true,reason:"humiModeHint",caps:{options:observed.options}};
  }
  observedHVAC(card) {
    const state=this._hass?.states?.[card?.entity_id],meta=this.entityFor(card?.entity_id)?.climate_hvac_mode,options=meta?.options;
    const known=["off","heat","cool","heat_cool","auto","dry","fan_only"];
    if (!card?.entity_id?.startsWith("climate.") || !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && known.includes(value)) || JSON.stringify(options)!==JSON.stringify(state?.attributes?.hvac_modes) || !options.includes(state?.state)) return null;
    return {options:[...options],index:options.indexOf(state.state)};
  }
  climateHVACAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"hvacUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_climate_hvac_mode!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedHVAC(card);
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="climate" || entity.available!==true || !observed ||
      !entity.actions?.some(action=>action?.service==="climate.set_hvac_mode")) return {ready:false,reason:"hvacEntity"};
    return {ready:true,reason:"hvacHint",caps:{options:observed.options}};
  }
  observedCoverTilt(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,d=this.entityFor(card?.entity_id)?.cover_tilt?.domain,features=attrs?.supported_features,value=attrs?.current_tilt_position;
    if (!card?.entity_id?.startsWith("cover.") || !["open","closed","opening","closing"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 128) ||
      d?.schema!=="numeric_steps_v1" || d.min!=="0" || d.max!=="100" || d.step!=="1" || d.unit!=="%" || d.max_index!==100 || !Number.isSafeInteger(value) || value<0 || value>100) return null;
    return {value,unit:"%",index:value};
  }
  coverTiltAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"coverTiltUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_cover_tilt!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("number") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("number")) return unsupported;
    const d=entity?.cover_tilt?.domain,field=entity?.actions?.find(action=>action?.service==="cover.set_cover_tilt_position")?.fields?.tilt_position;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="cover" || entity.available!==true || !this.observedCoverTilt(card) ||
      field?.type!=="number" || field.min!==0 || field.max!==100 || field.step!==1) return {ready:false,reason:"coverTiltEntity"};
    return {ready:true,reason:"coverTiltHint",caps:{domain:d}};
  }
  observedCoverPosition(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,d=this.entityFor(card?.entity_id)?.cover_position?.domain,features=attrs?.supported_features,value=attrs?.current_position;
    if (!card?.entity_id?.startsWith("cover.") || !["open","closed","opening","closing"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 4) ||
      d?.schema!=="numeric_steps_v1" || d.min!=="0" || d.max!=="100" || d.step!=="1" || d.unit!=="%" || d.max_index!==100 || !Number.isSafeInteger(value) || value<0 || value>100) return null;
    return {value,unit:"%",index:value};
  }
  coverPositionAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"coverPositionUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_cover_position!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("number") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("number")) return unsupported;
    const d=entity?.cover_position?.domain,field=entity?.actions?.find(action=>action?.service==="cover.set_cover_position")?.fields?.position;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="cover" || entity.available!==true || !this.observedCoverPosition(card) ||
      field?.type!=="number" || field.min!==0 || field.max!==100 || field.step!==1) return {ready:false,reason:"coverPositionEntity"};
    return {ready:true,reason:"coverPositionHint",caps:{domain:d}};
  }
  observedVacuumPower(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.vacuum_fan_speed,options=meta?.options,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("vacuum.") || !["cleaning","docked","idle","paused","returning","error"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 32) ||
      !Array.isArray(options) || options.length<1 || options.length>8 || new Set(options).size!==options.length ||
      !options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) ||
      JSON.stringify(options)!==JSON.stringify(attrs?.fan_speed_list)) return null;
    const index=options.indexOf(attrs?.fan_speed);
    return index>=0 ? {options:[...options],index} : null;
  }
  vacuumPowerAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"vacuumPowerUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_vacuum_fan_speed!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedVacuumPower(card),field=entity?.actions?.find(action=>action?.service==="vacuum.set_fan_speed")?.fields?.fan_speed;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="vacuum" || entity.available!==true || !observed || field?.type!=="select" ||
      JSON.stringify(field.options)!==JSON.stringify(observed.options)) return {ready:false,reason:"vacuumPowerEntity"};
    return {ready:true,reason:"vacuumPowerHint",caps:{options:observed.options}};
  }
  vacuumPowerLabel(value,options) {
    const names={quiet:"vacuumQuiet",silent:"vacuumSilent",normal:"vacuumNormal",standard:"vacuumStandard",turbo:"vacuumTurbo",eco:"vacuumEco",max:"vacuumMax",strong:"vacuumStrong",gentle:"vacuumGentle",off:"vacuumOff"};
    const labels=options.map(option=>names[option] ? this.t(names[option]) : option);
    return new Set(labels).size===labels.length ? labels[options.indexOf(value)] : value;
  }
  observedFanSpeed(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.fan_speed,options=meta?.options,count=meta?.speed_count,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("fan.") || !["on","off"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 1) ||
      !Number.isSafeInteger(count) || count<1 || count>7 || attrs?.percentage_step!==100/count || !Array.isArray(options) || options.length!==count+1 ||
      !options.every(value=>typeof value==="string" && /^(0|[1-9][0-9]{0,2})$/.test(value) && Number(value)<=100) || options[0]!=="0" || options[count]!=="100" ||
      !options.every((value,index)=>index===0 || Number(value)>Number(options[index-1])) || !Number.isSafeInteger(attrs?.percentage)) return null;
    const index=options.indexOf(String(attrs.percentage));
    return index>=0 ? {value:attrs.percentage,index,options:[...options],speed_count:count,percentage_step:attrs.percentage_step} : null;
  }
  fanSpeedAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"speedUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_fan_speed!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    const observed=this.observedFanSpeed(card),field=entity?.actions?.find(action=>action?.service==="fan.set_percentage")?.fields?.percentage;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="fan" || entity.available!==true || !observed ||
      field?.type!=="number" || field.min!==0 || field.max!==100) return {ready:false,reason:"speedEntity"};
    return {ready:true,reason:"speedHint",caps:{options:observed.options,speed_count:observed.speed_count,percentage_step:observed.percentage_step}};
  }
  observedColorTemperature(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.light_color_temperature,d=meta?.domain,modes=attrs?.supported_color_modes;
    if (!card?.entity_id?.startsWith("light.") || state?.state!=="on" || attrs?.color_mode!=="color_temp" || !Array.isArray(modes) || !modes.length || !modes.every(mode=>typeof mode==="string") || !modes.includes("color_temp") ||
      d?.schema!=="numeric_steps_v1" || d.unit!=="K" || d.step!=="1") return null;
    const values=[attrs.min_color_temp_kelvin,attrs.max_color_temp_kelvin,attrs.color_temp_kelvin];
    if (!values.every(Number.isSafeInteger) || values[0]<1000 || values[1]>20000 || values[0]>values[1] || values[2]<values[0] || values[2]>values[1] ||
      Number(d.min)!==values[0] || Number(d.max)!==values[1] || d.max_index!==values[1]-values[0]) return null;
    return {value:values[2],unit:"K",index:values[2]-values[0]};
  }
  lightColorTemperatureAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"kelvinUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_light_color_temperature!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("number") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("number")) return unsupported;
    const fields=entity?.actions?.find(action=>action?.service==="light.turn_on")?.fields?.color_temp_kelvin,d=entity?.light_color_temperature?.domain;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="light" || entity.available!==true || !this.observedColorTemperature(card) ||
      fields?.type!=="number" || fields.min!==Number(d?.min) || fields.max!==Number(d?.max) || fields.step!==1) return {ready:false,reason:"kelvinEntity"};
    return {ready:true,reason:"kelvinHint",caps:{domain:d}};
  }
  observedHumidity(card) {
    const climate=card?.entity_id?.startsWith("climate."),state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.[climate ? "climate_humidity" : "humidifier_humidity"],d=meta?.domain,features=attrs?.supported_features;
    if (!(climate || card?.entity_id?.startsWith("humidifier.")) || !(climate ? ["off","heat","cool","heat_cool","auto","dry","fan_only"] : ["on","off"]).includes(state?.state) ||
      climate && (!Number.isSafeInteger(features) || features<0 || !(features & 4)) || d?.schema!=="numeric_steps_v1" || d.unit!=="%") return null;
    const step=Object.hasOwn(attrs || {},"target_humidity_step") ? attrs.target_humidity_step : 1;
    const values=[attrs?.min_humidity,attrs?.max_humidity,step,attrs?.humidity];
    if (!values.every(Number.isSafeInteger) || values[0]<0 || values[1]>100 || values[0]>values[1] || step<=0 || values[3]<values[0] || values[3]>values[1] ||
      (values[3]-values[0])%step!==0 || Number(d.min)!==values[0] || Number(d.max)!==values[1] || Number(d.step)!==step || d.max_index!==Math.floor((values[1]-values[0])/step)) return null;
    return {value:values[3],unit:"%",index:(values[3]-values[0])/step};
  }
  climateHumidityAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"climateHumidityUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_climate_humidity!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("number") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("number")) return unsupported;
    const d=entity?.climate_humidity?.domain,field=entity?.actions?.find(action=>action?.service==="climate.set_humidity")?.fields?.humidity;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="climate" || entity.available!==true || !this.observedHumidity(card) ||
      field?.type!=="number" || field.min!==Number(d?.min) || field.max!==Number(d?.max) || field.step!==Number(d?.step)) return {ready:false,reason:"climateHumidityEntity"};
    return {ready:true,reason:"climateHumidityHint",caps:{domain:d}};
  }
  humidifierHumidityAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"humidityUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id);
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_humidifier_humidity!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("number") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("number")) return unsupported;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || entity?.domain!=="humidifier" || entity.available!==true || !this.observedHumidity(card) ||
      !entity.actions?.some(action=>action?.service==="humidifier.set_humidity")) return {ready:false,reason:"humidityEntity"};
    return {ready:true,reason:"humidityHint",caps:{domain:entity.humidifier_humidity.domain}};
  }
  observedTemperature(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.climate_temperature,d=meta?.domain,features=attrs?.supported_features;
    if (!card?.entity_id?.startsWith("climate.") || !["off","heat","cool","dry","fan_only"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 1) || (features & 2) ||
      d?.schema!=="numeric_steps_v1" || !["°C","°F"].includes(d.unit) || d.unit!==this._hass?.config?.unit_system?.temperature) return null;
    const values=[attrs.min_temp,attrs.max_temp,attrs.target_temp_step,attrs.temperature];
    if (!values.every(v=>typeof v==="number" && Number.isFinite(v))) return null;
    const micro=values.map(v=>Math.round(v*1e6));
    if (!micro.every((v,i)=>Number.isSafeInteger(v) && v/1e6===values[i]) || micro[2]<=0 || micro[0]>micro[1] || micro[3]<micro[0] || micro[3]>micro[1] || (micro[3]-micro[0])%micro[2]!==0 ||
      Number(d.min)!==values[0] || Number(d.max)!==values[1] || Number(d.step)!==values[2]) return null;
    const index=(micro[3]-micro[0])/micro[2];
    return Number.isSafeInteger(d.max_index) && index<=d.max_index ? {value:attrs.temperature,unit:d.unit,index} : null;
  }
  climateTemperatureAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"temperatureUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id];
    if (!this.isConnected || this._profileStale || this._statusError || this._hass?.connected===false || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_climate_temperature!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("number") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("number")) return unsupported;
    const attrs=state?.attributes,features=attrs?.supported_features,meta=entity?.climate_temperature,descriptor=meta?.domain;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || !card.entity_id.startsWith("climate.") || entity?.domain!=="climate" || entity.available!==true ||
      !Number.isSafeInteger(features) || features<0 || !(features & 1) || (features & 2)) return {ready:false,reason:"temperatureEntity"};
    if (!descriptor || descriptor.schema!=="numeric_steps_v1" || !["°C","°F"].includes(descriptor.unit) || descriptor.unit!==this._hass?.config?.unit_system?.temperature ||
      !this.observedTemperature(card) || typeof attrs.temperature!=="number" || !Number.isFinite(attrs.temperature) ||
      ![attrs.min_temp,attrs.max_temp,attrs.target_temp_step].every(value=>typeof value==="number" && Number.isFinite(value)) || attrs.target_temp_step<=0 ||
      !entity.actions?.some(action=>action?.service==="climate.set_temperature")) {
      const unit=this._hass?.config?.unit_system?.temperature;
      if ([1,2].includes(this._status.thermostat_version) && ["°C","°F"].includes(unit)) {
        return {ready:true,reason:"thermostatReadOnly",caps:{readOnly:true,unit}};
      }
      return {ready:false,reason:"temperatureEntity"};
    }
    return {ready:true,reason:"temperatureHint",caps:{domain:descriptor,metadata:{min:attrs.min_temp,max:attrs.max_temp,step:attrs.target_temp_step,unit:descriptor.unit}}};
  }
  fanDirectionAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported={ready:false,reason:"directionUnsupported"},slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id];
    const features=state?.attributes?.supported_features,options=entity?.fan_direction?.options,index=entity?.fan_direction?.index;
    if (this._profileStale || this._hass?.connected===false || this._statusError || this._status?.device_available!==true || this._status.entity_control_status!=="ready" ||
      this.profile?.schema_fan_direction!==true || !this.profile?.layout_versions?.includes(3) || !this.profile?.schema_control_types?.includes("choice") ||
      !this._status?.native_control_types?.includes("entity_control_v1") || !this._status?.control_kinds?.includes("choice")) return unsupported;
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || !card.entity_id.startsWith("fan.") || entity?.domain!=="fan" || entity.available!==true ||
      !["on","off"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features & 4) ||
      JSON.stringify(options)!==JSON.stringify(["forward","reverse"]) || !Number.isInteger(index) || index<0 || index>1 || options[index]!==state?.attributes?.direction ||
      !entity.actions?.some(action=>action?.service==="fan.set_direction")) return {ready:false,reason:"directionEntity"};
    return {ready:true,reason:"directionHint",caps:{options:[...options]}};
  }
  choiceControlAvailability(card=this.cardAt(this._selectedSlot)) {
    const unsupported = {ready:false,reason:this._profileStale ? "controlProfileChanged" : "choiceUnsupported"};
    if (this._profileStale || this._hass?.connected === false || this._status?.device_available !== true ||
      this._status.entity_control_status !== "ready" || (!Array.isArray(this._status.native_control_types) || !this._status.native_control_types.includes("entity_control_v1")) ||
      !Array.isArray(this._status.control_kinds) || !this._status.control_kinds.includes("choice") || !Array.isArray(this.profile?.schema_control_types) || !this.profile.schema_control_types.includes("choice") ||
      !Array.isArray(this.profile?.layout_versions) || !this.profile.layout_versions.includes(3)) return unsupported;
    const slot=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id];
    const options=entity?.choice_control?.options,index=entity?.choice_control?.index,domain=card?.entity_id?.split(".")[0];
    const fan=domain==="fan", current=fan ? state?.attributes?.preset_mode : state?.state, actualOptions=fan ? state?.attributes?.preset_modes : state?.attributes?.options, service=fan ? "fan.set_preset_mode" : `${domain}.select_option`;
    const fanSupported=!fan || (["on","off"].includes(state?.state) && Number.isSafeInteger(state?.attributes?.supported_features) && state.attributes.supported_features>=0 && !!(state.attributes.supported_features & (1|8)));
    const manual=fan && ["on","off"].includes(state?.state) && Object.hasOwn(state.attributes || {},"preset_mode") && current===null;
    const currentMatches=(Number.isInteger(index) && index>=0 && index<options?.length && options[index]===current) ||
      (manual && index===null && entity?.choice_control?.empty===true && this._status.empty_choice_version===1);
    const valid=Array.isArray(options) && options.length>=1 && options.length<=8 && new Set(options).size===options.length &&
      options.every(value=>typeof value==="string" && value.length>0 && !["unknown","unavailable"].includes(value) && new TextEncoder().encode(value).length<=32 && [...value].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char)));
    if (!card || card.type!=="entity" || !card.visible || !slot?.editable || slot.hidden || !this.isChoiceEntity(card) || entity?.domain!==domain || entity.available!==true ||
      !state || ["unknown","unavailable"].includes(state.state) || !valid || !currentMatches || !fanSupported ||
      JSON.stringify(actualOptions)!==JSON.stringify(options) || (!Array.isArray(entity.actions) || !entity.actions.some(item=>item?.service===service))) return {ready:false,reason:"choiceEntity"};
    return {ready:true,reason:"choiceHint",caps:{options:[...options]}};
  }
  controlText(key,kind="light") {
    if(kind==="statisticspanel") return this.t(({control:"statisticsControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"statisticsReview",controlReviewV3:"statisticsReview",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if(kind==="agendapanel") return this.t(({control:"agendaControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"agendaReview",controlReviewV3:"agendaReview",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if (kind==="textpanel") return this.t(({control:"textPanelControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"textPanelReview",controlReviewV3:"textPanelReview",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if (kind==="datetimepanel") return this.t(({control:"datetimePanelControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"datetimePanelReview",controlReviewV3:"datetimePanelReview",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if (kind==="actionparameterspanel") return this.t(({control:"actionParametersControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"actionParametersReview",controlReviewV3:"actionParametersReview",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if (kind==="actionpanel") return this.t(({control:"actionPanelControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"extraReviewV2",controlReviewV3:"extraReviewV3",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if (kind==="mediapanel") return this.t(({control:"mediaPanelControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"extraReviewV2",controlReviewV3:"extraReviewV3",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if (["infopanel","lockpanel"].includes(kind)) return this.t(({control:kind==="infopanel"?"infoPanelControl":"lockPanelControl",controlReviewTitle:"extraReviewTitle",controlReviewV2:"extraReviewV2",controlReviewV3:"extraReviewV3",controlConfirm:"extraConfirm",controlNotice:"extraNotice"})[key] || key);
    if (kind === "effect") {
      const names={control:"effectControl",controlReviewTitle:"effectReviewTitle",controlReviewV2:"effectReviewV2",controlReviewV3:"effectReviewV3",controlConfirm:"effectConfirm",controlNotice:"effectNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "covertilt") {
      const names={control:"coverTiltControl",controlReviewTitle:"coverTiltReviewTitle",controlReviewV2:"coverTiltReviewV2",controlReviewV3:"coverTiltReviewV3",controlConfirm:"coverTiltConfirm",controlNotice:"coverTiltNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "coverposition") {
      const names={control:"coverPositionControl",controlReviewTitle:"coverPositionReviewTitle",controlReviewV2:"coverPositionReviewV2",controlReviewV3:"coverPositionReviewV3",controlConfirm:"coverPositionConfirm",controlNotice:"coverPositionNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "mediarepeat") {
      const names={control:"mediaRepeatControl",controlReviewTitle:"mediaRepeatReviewTitle",controlReviewV2:"mediaRepeatReviewV2",controlReviewV3:"mediaRepeatReviewV3",controlConfirm:"mediaRepeatConfirm",controlNotice:"mediaRepeatNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "mediasource") {
      const names={control:"mediaSourceControl",controlReviewTitle:"mediaSourceReviewTitle",controlReviewV2:"mediaSourceReviewV2",controlReviewV3:"mediaSourceReviewV3",controlConfirm:"mediaSourceConfirm",controlNotice:"mediaSourceNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "mediasound") {
      const names={control:"mediaSoundControl",controlReviewTitle:"mediaSoundReviewTitle",controlReviewV2:"mediaSoundReviewV2",controlReviewV3:"mediaSoundReviewV3",controlConfirm:"mediaSoundConfirm",controlNotice:"mediaSoundNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "remoteactivity") {
      const names={control:"activityControl",controlReviewTitle:"activityReviewTitle",controlReviewV2:"activityReviewV2",controlReviewV3:"activityReviewV3",controlConfirm:"activityConfirm",controlNotice:"activityNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "vacuumfan") {
      const names={control:"vacuumPowerControl",controlReviewTitle:"vacuumPowerReviewTitle",controlReviewV2:"vacuumPowerReviewV2",controlReviewV3:"vacuumPowerReviewV3",controlConfirm:"vacuumPowerConfirm",controlNotice:"vacuumPowerNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "speed") {
      const names={control:"speedControl",controlReviewTitle:"speedReviewTitle",controlReviewV2:"speedReviewV2",controlReviewV3:"speedReviewV3",controlConfirm:"speedConfirm",controlNotice:"speedNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "kelvin") {
      const names={control:"kelvinControl",controlReviewTitle:"kelvinReviewTitle",controlReviewV2:"kelvinReviewV2",controlReviewV3:"kelvinReviewV3",controlConfirm:"kelvinConfirm",controlNotice:"kelvinNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "climatehumidity") {
      const names={control:"climateHumidityControl",controlReviewTitle:"climateHumidityReviewTitle",controlReviewV2:"climateHumidityReviewV2",controlReviewV3:"climateHumidityReviewV3",controlConfirm:"climateHumidityConfirm",controlNotice:"climateHumidityNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "humidity") {
      const names={control:"humidityControl",controlReviewTitle:"humidityReviewTitle",controlReviewV2:"humidityReviewV2",controlReviewV3:"humidityReviewV3",controlConfirm:"humidityConfirm",controlNotice:"humidityNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "preset") {
      const names={control:"presetControl",controlReviewTitle:"presetReviewTitle",controlReviewV2:"presetReviewV2",controlReviewV3:"presetReviewV3",controlConfirm:"presetConfirm",controlNotice:"presetNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "airflow") {
      const names={control:"airflowControl",controlReviewTitle:"airflowReviewTitle",controlReviewV2:"airflowReviewV2",controlReviewV3:"airflowReviewV3",controlConfirm:"airflowConfirm",controlNotice:"airflowNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "swing") {
      const names={control:"swingControl",controlReviewTitle:"swingReviewTitle",controlReviewV2:"swingReviewV2",controlReviewV3:"swingReviewV3",controlConfirm:"swingConfirm",controlNotice:"swingNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "horizontal") {
      const names={control:"horizontalControl",controlReviewTitle:"horizontalReviewTitle",controlReviewV2:"horizontalReviewV2",controlReviewV3:"horizontalReviewV3",controlConfirm:"horizontalConfirm",controlNotice:"horizontalNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "humidifier") {
      const names={control:"humiModeControl",controlReviewTitle:"humiModeReviewTitle",controlReviewV2:"humiModeReviewV2",controlReviewV3:"humiModeReviewV3",controlConfirm:"humiModeConfirm",controlNotice:"humiModeNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "hvac") {
      const names={control:"hvacControl",controlReviewTitle:"hvacReviewTitle",controlReviewV2:"hvacReviewV2",controlReviewV3:"hvacReviewV3",controlConfirm:"hvacConfirm",controlNotice:"hvacNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "temperature") {
      const names={control:"temperatureControl",controlReviewTitle:"temperatureReviewTitle",controlReviewV2:"temperatureReviewV2",controlReviewV3:"temperatureReviewV3",controlConfirm:"temperatureConfirm",controlNotice:"temperatureNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "direction") {
      const names={control:"directionControl",controlReviewTitle:"directionReviewTitle",controlReviewV2:"directionReviewV2",controlReviewV3:"directionReviewV3",controlConfirm:"directionConfirm",controlNotice:"directionNotice"};
      return this.t(names[key] || key);
    }
    if (["timerpanel","remotepanel","powerpanel"].includes(kind)) {
      const names={control:kind.slice(0,-5)+"PanelControl",controlReviewTitle:"panelReviewTitle",controlReviewV2:"panelReviewV2",controlReviewV3:"panelReviewV3",controlConfirm:"panelConfirm",controlNotice:"panelNotice"};
      return this.t(names[key] || key);
    }
    if (kind==="lightdetail" || kind==="climatepanel") {
      const names={control:kind==="lightdetail"?"lightDetailControl":"climatePanelControl",controlReviewTitle:"detailReviewTitle",controlReviewV2:"detailReviewV2",controlReviewV3:"detailReviewV3",controlConfirm:"detailConfirm",controlNotice:"detailNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "robot") {
      const names={control:"robotControl",controlReviewTitle:"robotReviewTitle",controlReviewV2:"robotReviewV2",controlReviewV3:"robotReviewV3",controlConfirm:"robotConfirm",controlNotice:"robotNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "humiditypanel") {
      const names={control:"humidityPanelControl",controlReviewTitle:"humidityPanelReviewTitle",controlReviewV2:"humidityPanelReviewV2",controlReviewV3:"humidityPanelReviewV3",controlConfirm:"humidityPanelConfirm",controlNotice:"humidityPanelNotice"};
      return this.t(names[key] || key);
    }
    if (kind === "fan") {
      const names={control:"fanControl",controlReviewTitle:"fanReviewTitle",controlReviewV2:"fanReviewV2",controlReviewV3:"fanReviewV3",controlConfirm:"fanConfirm",controlNotice:"fanNotice"};
      return this.t(names[key] || key);
    }
    const number = {control:"numberControl",controlReviewTitle:"numberReviewTitle",controlReviewV2:"numberReviewV2",controlReviewV3:"numberReviewV3",controlConfirm:"numberConfirm",controlNotice:"numberNotice"};
    const choice = {control:"choiceControl",controlReviewTitle:"choiceReviewTitle",controlReviewV2:"choiceReviewV2",controlReviewV3:"choiceReviewV3",controlConfirm:"choiceConfirm",controlNotice:"choiceNotice"};
    if (kind === "cover" && this._status?.cover_panel_version===1) {
      const names={control:"coverPanelControl",controlReviewTitle:"coverPanelReviewTitle",controlReviewV2:"coverPanelReviewV2",controlReviewV3:"coverPanelReviewV3",controlConfirm:"coverPanelConfirm",controlNotice:"coverPanelNotice"};
      return this.t(names[key] || key);
    }
    const cover = {control:"coverControl",controlReviewTitle:"coverReviewTitle",controlReviewV2:"coverReviewV2",controlReviewV3:"coverReviewV3",controlConfirm:"coverConfirm",controlNotice:"coverNotice"};
    return this.t(kind === "number" && number[key] ? number[key] : kind === "choice" && choice[key] ? choice[key] : kind === "cover" && cover[key] ? cover[key] : key);
  }
  paintControlAvailability() {
    // Do not replace a field under the user's cursor. Admission is rechecked
    // on selection and confirmation, including when a displayed option is old.
    if (!this.shadowRoot.querySelector(".inspector")?.contains(this.shadowRoot.activeElement)) this.paintInspector();
    if (["light-control","tile-event","camera-preview"].includes(this._pending?.kind)) this.renderModal();
  }
  validCameraPreview(card) {
    const action=card?.action;
    return this.profile?.schema_camera_preview===true && card?.type==="entity" && card.entity_id?.startsWith("camera.") &&
      action?.kind==="camera_preview" && Object.keys(action).length===2 && Number.isInteger(action.duration_seconds) && action.duration_seconds>=15 && action.duration_seconds<=90;
  }
  cameraPreviewAvailability(card=this.cardAt(this._selectedSlot)) {
    const place=this.slotAt(card?.slot),entity=this.entityFor(card?.entity_id),state=this._hass?.states?.[card?.entity_id];
    return !!(this.isConnected && !this._statusError && !this._profileStale && this.profile?.schema_camera_preview===true &&
      this.profile?.layout_versions?.includes(3) && this._status.device_available===true && this._status.camera_preview_supported===true &&
      this._status.context_press_version===1 && this._status.press_enabled_version===1 && Number.isSafeInteger(this._status.camera_catalog_generation) &&
      this._status.camera_preview_entities?.includes(card?.entity_id) && this._status.sent_revision===this._saved?.revision &&
      entity?.camera_preview?.allowlisted===true && !this.entityMetadataStale(entity) && state && !["unknown","unavailable"].includes(state.state) &&
      card?.type==="entity" && card.visible===true && card.entity_id.startsWith("camera.") && place?.editable===true && place.hidden!==true && place.slot>=2);
  }
  cameraPreviewStatusKey() {
    return JSON.stringify([this.cameraPreviewAvailability(),this._status.camera_catalog_generation,this._status.camera_preview_entities]);
  }
  requestCameraPreview() {
    this.finishField();
    const card=this.cardAt(this._selectedSlot);
    if(this._busy || this._pending || this._conflict || this._drag || this._carry || this._selectingCards || Object.keys(this._fieldErrors).length || !this.cameraPreviewAvailability(card)) return false;
    this._pending={kind:"camera-preview",entryId:this._entryId,epoch:this._selectionEpoch,user:this._hass?.user?.id,slot:card.slot,cardId:card.id,
      savedRevision:this._saved?.revision,layout:AEH_COMPARE(this._draft),profile:JSON.stringify(this.profile),generation:this._status.camera_catalog_generation,
      state:this._hass.states[card.entity_id],duration:this.validCameraPreview(card)?card.action.duration_seconds:35};
    this.paintInspector();this.renderModal();return true;
  }
  cameraPreviewReviewCurrent() {
    const p=this._pending,card=this.cardAt(p?.slot);
    return p?.kind==="camera-preview" && !this._conflict && !this._drag && !this._carry && !this._selectingCards && !Object.keys(this._fieldErrors).length &&
      p.entryId===this._entryId && p.epoch===this._selectionEpoch && p.user===this._hass?.user?.id && p.slot===this._selectedSlot && p.cardId===card?.id &&
      p.savedRevision===this._saved?.revision && p.layout===AEH_COMPARE(this._draft) && p.profile===JSON.stringify(this.profile) &&
      p.generation===this._status.camera_catalog_generation && p.state===this._hass?.states?.[card?.entity_id] && this.cameraPreviewAvailability(card);
  }
  cameraPreviewDurationValid() { const n=this._pending?.duration;return Number.isInteger(n) && n>=15 && n<=90; }
  confirmCameraPreview() {
    const pending=this._pending;
    if(this._busy || pending?.kind!=="camera-preview") return false;
    if(!this.cameraPreviewReviewCurrent() || !this.cameraPreviewDurationValid()) {
      this._pending=null;this._error=this.t("tileEventChanged");this.paintInspector();this.renderModal();this.paintFeedback();return false;
    }
    this._pending=null;
    return this.mutate(layout=>{layout.version=3;this.cardAt(pending.slot).action={kind:"camera_preview",duration_seconds:pending.duration};});
  }
  isTileEventPanel(card) {
    const a=card?.action;
    return card?.type==="action" && card.entity_id==="" && a?.kind==="control" && a.control==="panel" && a.property==="tile_event" && Object.keys(a).length===3;
  }
  validTileEventPanel(card) {
    return this.isTileEventPanel(card) && this.profile?.layout_versions?.includes(3) && this.profile?.schema_control_types?.includes("panel") &&
      ["action","tile_event"].every(name=>this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,name));
  }
  tileEventPanelAvailability(slot=this._selectedSlot) {
    const place=this.slotAt(slot),card=this.cardAt(slot);
    return this.isConnected && !this._statusError && !this._profileStale && this._status.device_available===true &&
      this._status.entity_control_status==="ready" && this._status.native_control_types?.includes("panel") &&
      this.profile?.schema_control_types?.includes("panel") && this.profile?.layout_versions?.includes(3) &&
      ["action","tile_event"].every(name=>this.hasExtraProfile(this.profile?.schema_panel_extra_profiles,name) && this.hasExtraProfile(this._status.panel_extra_profiles,name)) &&
      place?.editable===true && place.hidden!==true && place.slot>=2 && place.types.includes("action") && (!card || card.type==="action");
  }
  eventAvailability(slot=this._selectedSlot) {
    const place = this.slotAt(slot), card = this.cardAt(slot);
    return this.isConnected && !this._statusError && !this._profileStale && this.profile?.schema_event_actions === true &&
      Array.isArray(this.profile.layout_versions) && this.profile.layout_versions.includes(3) &&
      this._status.device_available === true && this._status.event_press_supported === true &&
      place?.editable === true && place.hidden !== true && place.slot >= 2 && place.types.includes("action") && (!card || card.type === "action");
  }
  stateLabelsEligible(card) {
    return card?.type === "sensor" && ["sensor","binary_sensor","number","input_number","select","input_select","input_text","input_datetime"].includes(card.entity_id?.split(".")[0]) && Number.isInteger(card.slot) && card.slot >= 2 && card.slot < 16;
  }
  labelsFromRows(rows) {
    if (!Array.isArray(rows) || rows.length > 8) return null;
    const keys = new Set();
    for (const row of rows) {
      if (!row || typeof row !== "object" || ["unknown","unavailable"].includes(row.key) || keys.has(row.key)) return null;
      for (const text of [row.key,row.label]) {
        if (typeof text !== "string" || !text.trim() || /[\p{C}\p{Z}]/u.test(text.replaceAll(" ","")) || new TextEncoder().encode(text).length > 32) return null;
      }
      keys.add(row.key);
    }
    return Object.fromEntries(rows.map(row=>[row.key,row.label]));
  }
  requestStateLabels() {
    this.finishField();
    const card = this.cardAt(this._selectedSlot);
    if (this._busy || this._pending || this._conflict || this._profileStale || this._drag || this._carry || this._selectingCards || Object.keys(this._fieldErrors).length || this.profile.schema_state_labels !== true || !this.stateLabelsEligible(card)) return false;
    this._pending = {kind:"state-labels",entryId:this._entryId,epoch:this._selectionEpoch,user:this._hass?.user?.id,slot:card.slot,cardId:card.id,
      savedRevision:this._saved?.revision,layout:AEH_COMPARE(this._draft),profile:JSON.stringify(this.profile),rows:Object.entries(card.state_labels || {}).map(([key,label])=>({key,label}))};
    this.renderModal(); return true;
  }
  stateLabelsReviewCurrent() {
    const pending = this._pending, card = this.cardAt(pending?.slot);
    return pending?.kind === "state-labels" && !this._conflict && !this._profileStale && !this._drag && !this._carry && !this._selectingCards &&
      pending.entryId === this._entryId && pending.epoch === this._selectionEpoch && pending.user === this._hass?.user?.id && pending.slot === this._selectedSlot && pending.cardId === card?.id &&
      pending.savedRevision === this._saved?.revision && pending.layout === AEH_COMPARE(this._draft) && pending.profile === JSON.stringify(this.profile) && this.stateLabelsEligible(card);
  }
  editStateLabel(index, part, value) {
    if (this._busy || !this.stateLabelsReviewCurrent() || !Number.isInteger(index) || !this._pending.rows[index] || !["key","label"].includes(part)) return false;
    this._pending.rows[index][part] = value;
    const invalid = this.labelsFromRows(this._pending.rows) === null, error = this.shadowRoot.querySelector("[data-labels-error]");
    if (error) error.textContent = invalid ? this.t("stateLabelsInvalid") : "";
    this.paintToolbar(); return true;
  }
  addStateLabel() {
    if (this._busy || !this.stateLabelsReviewCurrent() || this._pending.rows.length >= 8) return false;
    this._pending.rows.push({key:"",label:""});this.renderModal();
    this.shadowRoot.querySelector(`[data-label-index="${this._pending.rows.length-1}"][data-label-part="key"]`)?.focus(); return true;
  }
  removeStateLabel(index) {
    if (this._busy || !this.stateLabelsReviewCurrent() || !Number.isInteger(index) || !this._pending.rows[index]) return false;
    this._pending.rows.splice(index,1);this.renderModal();return true;
  }
  confirmStateLabels() {
    if (this._busy || this._pending?.kind !== "state-labels") return false;
    const labels = this.labelsFromRows(this._pending.rows);
    if (!this.stateLabelsReviewCurrent() || labels === null) {
      this._error = this.t(labels === null ? "stateLabelsInvalid" : "stateLabelsChanged");this.paintFeedback();return false;
    }
    const card = this.cardAt(this._pending.slot);this._pending = null;
    const changed = this.mutate(()=>{if (Object.keys(labels).length) card.state_labels = labels;else delete card.state_labels;});
    this.renderModal();if (changed) { this._notice = this.t("stateLabelsNotice");this.paintFeedback(); }return changed;
  }
  requestTileEvent(panel=false) {
    if (this._selectingCards) return false;
    this.finishField();
    const card = this.cardAt(this._selectedSlot);
    if (this._busy || this._pending || this._conflict || this._drag || this._carry || Object.keys(this._fieldErrors).length || ![2,3].includes(this._draft?.version) || !(panel?this.tileEventPanelAvailability():this.eventAvailability()) || (panel?this.isTileEventPanel(card):card?.action?.kind === "event")) { this.paintInspector(); return false; }
    this._pending = {kind:"tile-event",panel,entryId:this._entryId,epoch:this._selectionEpoch,user:this._hass?.user?.id,
      cardId:card?.id ?? null,slot:this._selectedSlot,savedRevision:this._saved?.revision,draftRevision:this._draft.revision,layout:AEH_COMPARE(this._draft),profile:JSON.stringify(this.profile)};
    this.paintInspector(); this.renderModal(); return true;
  }
  tileEventReviewCurrent() {
    const pending = this._pending;
    return pending?.kind === "tile-event" && !this._conflict && !this._drag && !this._carry && !this._selectingCards && !Object.keys(this._fieldErrors).length &&
      pending.entryId === this._entryId && pending.epoch === this._selectionEpoch && pending.user === this._hass?.user?.id &&
      pending.slot === this._selectedSlot && pending.cardId === (this.cardAt(pending.slot)?.id ?? null) && pending.layout === AEH_COMPARE(this._draft) &&
      pending.savedRevision === this._saved?.revision && pending.draftRevision === this._draft?.revision && pending.profile === JSON.stringify(this.profile) && (pending.panel?this.tileEventPanelAvailability(pending.slot):this.eventAvailability(pending.slot));
  }
  confirmTileEvent() {
    const pending = this._pending;
    if (pending?.kind !== "tile-event" || this._busy) return false;
    if (!this.tileEventReviewCurrent()) {
      this._pending = null; this._error = this.t("tileEventChanged"); this.paintInspector(); this.renderModal(); this.paintFeedback(); return false;
    }
    const existing = this.cardAt(pending.slot);
    const card = existing || {id:`card-${AEH_UUID()}`,slot:Number(pending.slot),type:"action",title:this.t("tileEventTitle"),icon:"action",palette:"primary",visible:true};
    this._pending = null;
    const changed = this.mutate(layout => {
      layout.version = 3; card.entity_id = ""; card.action = pending.panel?{kind:"control",control:"panel",property:"tile_event"}:{kind:"event"}; delete card.state_color; delete card.display_precision; delete card.state_labels;
      if (!existing) layout.cards.push(card);
    });
    if (changed) { this._notice = this.t("tileEventNotice"); this.paintFeedback(); }
    return changed;
  }
  panelActionDraft(card,family,policies=null) {
    const action={kind:"control",control:"panel",property:family};
    if(family==="action" && this.actionPanelDomain(card)==="automation") Object.assign(action,policies || this.actionPanelPolicies(card));
    const prior=card.action?.kind==="service" && card.action.service==="timer.start" ? card.action.data?.duration : card.action?.initial_duration;
    if (family==="timer" && Number.isInteger(prior) && prior>=1 && prior<=86400) action.initial_duration=prior;
    return action;
  }
  requestLightControl(controlKind="light",actionPolicies=null) {
    if (this._selectingCards) return false;
    this.finishField();
    const card = this.cardAt(this._selectedSlot);
    if (this._busy || this._pending || this._conflict || this._drag || this._carry || Object.keys(this._fieldErrors).length || ![2,3].includes(this._draft?.version) || !["textpanel","datetimepanel","actionpanel","actionparameterspanel","mediapanel","agendapanel","statisticspanel","infopanel","lockpanel","lightdetail","climatepanel","timerpanel","remotepanel","powerpanel","light","number","choice","cover","fan","humiditypanel","robot","direction","temperature","hvac","preset","airflow","swing","horizontal","humidifier","humidity","effect","kelvin","speed","climatehumidity","vacuumfan","coverposition","covertilt","remoteactivity","mediasource","mediarepeat","mediasound"].includes(controlKind) || !this.controlAvailability(card,controlKind).ready) { this.paintInspector(); return false; }
    const property={statisticspanel:"statistics",agendapanel:"agenda",textpanel:"text",datetimepanel:"datetime",actionpanel:"action",actionparameterspanel:"action",mediapanel:"media",infopanel:"info",lockpanel:"lock",climatepanel:"climate",timerpanel:"timer",remotepanel:"remote",powerpanel:"power",mediasound:"sound_mode",mediarepeat:"repeat",mediasource:"source",remoteactivity:"activity",covertilt:"tilt_position",coverposition:"position",vacuumfan:"fan_speed",climatehumidity:"humidity",speed:"percentage",kelvin:"color_temp_kelvin",effect:"effect",direction:"direction",temperature:"temperature",humidity:"humidity",hvac:"hvac_mode",preset:"preset_mode",airflow:"fan_mode",swing:"swing_mode",horizontal:"swing_horizontal_mode",humidifier:"mode"}[controlKind];
    if (controlKind==="lightdetail" && card.action.kind==="control" && card.action.control==="light" && card.action.detail===1) return false;
    if (actionPolicies!==null && (controlKind!=="actionpanel" || this.actionPanelDomain(card)!=="automation" || Object.keys(actionPolicies).length!==2 || typeof actionPolicies.skip_condition!=="boolean" || typeof actionPolicies.stop_actions!=="boolean")) return false;
    if (actionPolicies===null && controlKind!=="lightdetail" && card.action.kind === "control" && (property ? card.action.property === property && (controlKind==="actionparameterspanel" ? this.isActionParametersAction(card) : controlKind!=="actionpanel" || this.isActionPanelAction(card)) : card.action.control === (controlKind === "humiditypanel" ? "humidifier" : controlKind) && !card.action.property)) return false;
    this._pending = {kind:"light-control",controlKind,actionPolicies:actionPolicies || (controlKind==="actionpanel"?this.actionPanelPolicies(card):null),entryId:this._entryId,epoch:this._selectionEpoch,user:this._hass?.user?.id,
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
    const changed = this.mutate(layout => { layout.version = 3; if(["textpanel","datetimepanel"].includes(controlKind)) { card.type="entity"; delete card.state_labels; delete card.display_precision; delete card.state_color; if(card.icon==="auto")card.icon=controlKind==="textpanel"?"action":"clock"; } card.action = controlKind==="actionparameterspanel" ? {kind:"control",control:"panel",property:"action",parameters:"boolean_v1"} : controlKind==="lightdetail" ? {kind:"control",control:"light",detail:1} : controlKind==="climatepanel" ? {kind:"control",control:"panel",property:"climate"} : ["textpanel","datetimepanel","actionpanel","actionparameterspanel","mediapanel","agendapanel","statisticspanel","infopanel","lockpanel","timerpanel","remotepanel","powerpanel"].includes(controlKind) ? this.panelActionDraft(card,controlKind.slice(0,-5),pending.actionPolicies) : controlKind === "humiditypanel" ? {kind:"control",control:"humidifier"} : controlKind === "mediasound" ? {kind:"control",control:"choice",property:"sound_mode"} : controlKind === "mediarepeat" ? {kind:"control",control:"choice",property:"repeat"} : controlKind === "mediasource" ? {kind:"control",control:"choice",property:"source"} : controlKind === "remoteactivity" ? {kind:"control",control:"choice",property:"activity"} : controlKind === "covertilt" ? {kind:"control",control:"number",property:"tilt_position"} : controlKind === "coverposition" ? {kind:"control",control:"number",property:"position"} : controlKind === "vacuumfan" ? {kind:"control",control:"choice",property:"fan_speed"} : controlKind === "climatehumidity" ? {kind:"control",control:"number",property:"humidity"} : controlKind === "speed" ? {kind:"control",control:"choice",property:"percentage"} : controlKind === "kelvin" ? {kind:"control",control:"number",property:"color_temp_kelvin"} : controlKind === "effect" ? {kind:"control",control:"choice",property:"effect"} : controlKind === "direction" ? {kind:"control",control:"choice",property:"direction"} : controlKind === "humidity" ? {kind:"control",control:"number",property:"humidity"} : controlKind === "temperature" ? {kind:"control",control:"number",property:"temperature"} : controlKind === "hvac" ? {kind:"control",control:"choice",property:"hvac_mode"} : controlKind === "preset" ? {kind:"control",control:"choice",property:"preset_mode"} : controlKind === "airflow" ? {kind:"control",control:"choice",property:"fan_mode"} : controlKind === "swing" ? {kind:"control",control:"choice",property:"swing_mode"} : controlKind === "horizontal" ? {kind:"control",control:"choice",property:"swing_horizontal_mode"} : controlKind === "humidifier" ? {kind:"control",control:"choice",property:"mode"} : {kind:"control",control:controlKind}; });
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
      if(input.dataset?.field==="data:volume_level" && this.cardAt(this._selectedSlot)?.action?.service==="media_player.volume_set") {
        const percent=Number(value);
        if(!value.trim() || !Number.isFinite(percent) || percent<0 || percent>100)throw new Error(this.t("checkNumber"));
        return percent/100;
      }
      const number = Number(value);
      if (!Number.isFinite(number) || (descriptor.min !== undefined && number < descriptor.min) || (descriptor.max !== undefined && number > descriptor.max)) throw new Error(this.t("checkNumber"));
      if (input.dataset?.field === "data:duration" && !Number.isInteger(number)) throw new Error(this.t("checkNumber"));
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
    if (input.dataset?.field==="action-kind" && input.value==="camera_preview") { this.requestCameraPreview();return; }
    if (input.dataset?.field?.startsWith("action-policy-")) { this.requestActionPanelPolicy(input.dataset.field.slice(14),input.checked); this.paintInspector(); return; }
    if (input.dataset?.field==="vacuum-area") { this.configureVacuumArea(input.value); return; }
    if (this._selectingCards) return;
    if (this._busy) return;
    const card = this.cardAt(this._selectedSlot); if (!card) return;
    if (input.dataset.field === "action-kind" && input.value === "tile-event-panel") { this.requestTileEvent(true); return; }
    if (input.dataset.field === "action-kind" && input.value === "event") { this.requestTileEvent(); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-direction") { this.requestLightControl("direction"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-effect") { this.requestLightControl("effect"); return; }
    if (input.dataset.field === "action-kind" && ["control-textpanel","control-datetimepanel","control-actionpanel","control-actionparameterspanel","control-mediapanel","control-agendapanel","control-statisticspanel","control-infopanel","control-lockpanel","control-timerpanel","control-remotepanel","control-powerpanel"].includes(input.value)) { this.requestLightControl(input.value.slice(8)); return; }
    if (input.dataset.field === "action-kind" && ["control-lightdetail","control-climatepanel"].includes(input.value)) { this.requestLightControl(input.value.slice(8)); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-robot") { this.requestLightControl("robot"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-humiditypanel") { this.requestLightControl("humiditypanel"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-fan") { this.requestLightControl("fan"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-covertilt") { this.requestLightControl("covertilt"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-coverposition") { this.requestLightControl("coverposition"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-mediarepeat") { this.requestLightControl("mediarepeat"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-mediasound") { this.requestLightControl("mediasound"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-mediasource") { this.requestLightControl("mediasource"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-remoteactivity") { this.requestLightControl("remoteactivity"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-vacuumfan") { this.requestLightControl("vacuumfan"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-speed") { this.requestLightControl("speed"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-kelvin") { this.requestLightControl("kelvin"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-climatehumidity") { this.requestLightControl("climatehumidity"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-humidity") { this.requestLightControl("humidity"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-temperature") { this.requestLightControl("temperature"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-hvac") { this.requestLightControl("hvac"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-preset") { this.requestLightControl("preset"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-airflow") { this.requestLightControl("airflow"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-swing") { this.requestLightControl("swing"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-horizontal") { this.requestLightControl("horizontal"); return; }
    if (input.dataset.field === "action-kind" && input.value === "control-humidifier") { this.requestLightControl("humidifier"); return; }
    if (input.dataset.field === "action-kind" && ["control","control-number","control-choice","control-cover"].includes(input.value)) { this.requestLightControl(input.value === "control-number" ? "number" : input.value === "control-choice" ? "choice" : input.value === "control-cover" ? "cover" : "light"); return; }
    if (!this._fieldBefore) this._fieldBefore = AEH_CLONE(this._draft);
    const field = input.dataset.field;
    try {
      if (field === "panel-duration") {
        if (!this.validPanelAction(card) || card.action.property!=="timer") return;
        if (input.value==="") delete card.action.initial_duration;
        else { const n=Number(input.value); if (!/^[0-9]+$/.test(input.value) || !Number.isInteger(n) || n<1 || n>86400) throw new Error(this.t("checkNumber")); card.action.initial_duration=n; }
      }
      else if (field === "visible") card.visible = input.checked;
      else if (field === "state_color") { if (input.checked && this.stateColorEligible(card)) card.state_color = true; else delete card.state_color; }
      else if (field === "display_precision") {
        if (input.value === "") delete card.display_precision;
        else { const precision = Number(input.value); if (!this.precisionEligible(card) || !/^[0-6]$/.test(input.value)) throw new Error(this.t("checkNumber")); card.display_precision = precision; }
      }
      else if (field === "type") { card.type = input.value; if (!this.stateColorEligible(card)) delete card.state_color; if (!this.precisionEligible(card)) delete card.display_precision; if (!this.stateLabelsEligible(card)) delete card.state_labels; if (card.icon === "auto" && !this.autoIconEligible(card)) card.icon = "sensor"; if (!this.isTileEventPanel(card) && !this.isActionPanelAction(card) && !this.isActionParametersAction(card) && !this.isAgendaAction(card) && !this.isExtraPanelAction(card) && (card.type === "sensor" || (card.type !== "entity" && ["control","camera_preview"].includes(card.action.kind)) || (card.type !== "action" && card.action.kind === "event"))) card.action = {kind:"none"}; }
      else if (field === "action-kind") {
        if (card.type==="sensor" && input.value!=="none") return;
        if (this.isExtraPanelAction(card) && this.isCalendarCard(card) &&
          !this.acceptsCard(this.slotAt(card.slot),{...card,action:{kind:input.value}})) { this.refuseTextPlacement(card); return; }
        if (input.value === "fan_oscillation") {
          if (!this.fanOscillationReady(card)) return;
          this._draft.version = 3;
        }
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
    if (input.dataset?.cameraDuration!==undefined && this._pending?.kind==="camera-preview") {
      this._pending.duration=/^[0-9]{1,2}$/.test(input.value)?Number(input.value):null;this.paintToolbar();return;
    }
    if (input.dataset?.labelIndex !== undefined) return this.editStateLabel(Number(input.dataset.labelIndex),input.dataset.labelPart,input.value);
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
    if (action === "media-stop-configure") return this.configureMediaStop();
    if (action === "media-volume-target-configure") return this.configureMediaVolumeTarget();
    if (action === "media-volume-configure") return this.configureMediaVolume(button.dataset.operation);
    if (action === "media-shuffle-configure") return this.configureMediaShuffle(button.dataset.shuffled==="true");
    if (action === "media-mute-configure") return this.configureMediaMute(button.dataset.muted==="true");
    if (action === "remote-configure") return this.configureRemotePower(button.dataset.operation);
    if (action === "mower-configure") return this.configureMowerAction(button.dataset.operation);
    if (action === "vacuum-configure") return this.configureVacuumAction(button.dataset.operation);
    if (action === "vacuum-rooms-refresh") { await this.fetchSelectedEntity(true); this.paintInspector(); return; }
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
    if (action.startsWith("carousel-")) return this.editCarousel(action, button.dataset.page);
    if (action === "remove") return this.removeCard();
    if (action === "create-tile-event-panel") return this.requestTileEvent(true);
    if (action === "create-tile-event") return this.requestTileEvent();
    if (action === "state-labels") return this.requestStateLabels();
    if (action === "state-label-add") return this.addStateLabel();
    if (action === "state-label-remove") return this.removeStateLabel(Number(button.dataset.index));
    if (action === "modal-state-labels") return this.confirmStateLabels();
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
    if (action === "camera-preview-configure") return this.requestCameraPreview();
    if (action === "modal-camera-preview") return this.confirmCameraPreview();
    if (action === "modal-tile-event") return this.confirmTileEvent();
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
        const buttons = [...this.shadowRoot.querySelectorAll(this._pending.kind === "state-labels" ? ".modal input:not([disabled]),.modal button:not([disabled])" : ["group-paste","bulk-style"].includes(this._pending.kind) ? ".modal select:not([disabled]),.modal button:not([disabled])" : ".modal button:not([disabled])")];
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

  precisionEligible(card) {
    return card?.type === "sensor" && ["sensor","number","input_number"].includes(card.entity_id?.split(".")[0]);
  }
  durationStateText(card,state) {
    if (!card?.entity_id?.startsWith("sensor.") || state?.attributes?.device_class!=="duration") return null;
    const unit=typeof state.attributes.unit_of_measurement==="string" ? state.attributes.unit_of_measurement.trim() : "";
    if (!Object.hasOwn(AEH_DURATION_UNITS,unit)) return null;
    const raw=typeof state.state==="string" ? state.state.replace(/^[\p{White_Space}\u001c-\u001f]+|[\p{White_Space}\u001c-\u001f]+$/gu,"") : "";
    const match=/^([+-]?)(?:([0-9]+)(?:\.([0-9]*))?|\.([0-9]+))(?:[eE]([+-]?[0-9]+))?$/.exec(raw);
    if (!match) return this.t("unknown");
    if(raw.length>128) return this.t("outOfRange");
    const fraction=match[3] ?? match[4] ?? "",digits=((match[2] || "0")+fraction).replace(/^0+/,""),exponent=match[5] || "0";
    if(exponent.replace(/^[+-]?0*/,"").length>18) return this.t("outOfRange");
    const length=digits.length+Number(exponent)-fraction.length;
    if(digits && (length>16 || length===16 && (digits[0]!=="1" || /[1-9]/.test(digits.slice(1))))) return this.t("outOfRange");
    // Core's public display-registry entry represents the sensor option, with
    // source precision as the fallback. A card's numeric override is ignored
    // for durations, just as it is by the existing native projection.
    const registry=this._hass.entities?.[card.entity_id],observed=registry?.display_precision ?? registry?.dp;
    const precision=Number.isInteger(observed) ? Math.max(0,Math.min(6,observed)) : Math.max(0,Math.min(6,fraction.length-Number(exponent)));
    const polish=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl");
    const key=`en:${precision}`;
    try {
      if(!this._precisionFormats.has(key)) this._precisionFormats.set(key,new Intl.NumberFormat("en",{useGrouping:false,minimumFractionDigits:precision,maximumFractionDigits:precision,roundingMode:"halfEven"}));
      const formatter=this._precisionFormats.get(key);if(formatter.resolvedOptions().roundingMode!=="halfEven") return null;
      let rounded=formatter.format(!digits || length < -6 ? "0" : raw);
      if(!/^-?[0-9]+(?:\.[0-9]+)?$/.test(rounded)) return this.t("unknown");
      if(/^-0(?:\.0+)?$/.test(rounded)) rounded=rounded.slice(1);
      const negative=rounded.startsWith("-"),parts=rounded.replace(/^-/,"").split("."),[multiplier,unitScale]=AEH_DURATION_UNITS[unit];
      const scale=(parts[1]?.length || 0)+unitScale,denominator=10n**BigInt(scale);
      let remaining=BigInt(parts.join(""))*multiplier;
      if(remaining>316224000n*denominator) return this.t("outOfRange");
      if(remaining>0n && remaining<denominator) return `${polish?rounded.replace(".",","):rounded} ${unit==="μs"?"us":unit}`;
      const result=[];
      for(const [seconds,suffix]of [[86400n,"d"],[3600n,"h"],[60n,"min"]]) {
        const count=remaining/(seconds*denominator);remaining%=seconds*denominator;
        if(count) result.push(`${count} ${suffix}`);
        if(result.length===2) break;
      }
      if(result.length<2 && (remaining>0n || !result.length)) {
        const places=Math.min(6,scale),divisor=10n**BigInt(scale-places),remainder=remaining%divisor;
        let value=remaining/divisor;
        if(remainder*2n>divisor || remainder*2n===divisor && value%2n===1n) value++;
        const base=10n**BigInt(places),seconds=(value/base).toString(),fraction=(value%base).toString().padStart(places,"0");
        result.push(`${seconds}${places?(polish?",":".")+fraction:""} s`);
      }
      return `${negative?"-":""}${result.join(" ")}`.slice(0,40);
    } catch {return this.t("unknown");}
  }
  precisionStateText(card,state) {
    const precision = card.display_precision;
    if (!this.precisionEligible(card) || !Number.isInteger(precision) || precision < 0 || precision > 6 ||
        ["duration","enum","date","timestamp","uptime"].includes(state.attributes?.device_class)) return null;
    const raw = typeof state.state === "string" ? state.state.trim() : "";
    if (raw.length > 128) return this.t("outOfRange");
    const match = /^([+-]?)(?:([0-9]+)(?:\.([0-9]*))?|\.([0-9]+))(?:[eE]([+-]?[0-9]+))?$/.exec(raw);
    if (!match) return null;
    const fraction = match[3] ?? match[4] ?? "", digits = ((match[2] || "0")+fraction).replace(/^0+/,"");
    const exponent = match[5] || "0", exponentDigits = exponent.replace(/^[+-]?0*/,"");
    if (exponentDigits.length > 18) return this.t("outOfRange");
    const length = digits.length + Number(exponent) - fraction.length;
    if (digits && (length > 16 || (length === 16 && (digits[0] !== "1" || /[1-9]/.test(digits.slice(1)))))) return this.t("outOfRange");
    const unit = state.attributes?.unit_of_measurement;
    if (unit !== undefined && typeof unit !== "string") return null;
    if (unit && /[<>&]/.test(unit)) return null;
    const locale = this._hass?.locale?.language?.startsWith("pl") || this._hass?.language?.startsWith("pl") ? "pl" : "en";
    const key = `${locale}:${precision}`;
    try {
      if (!this._precisionFormats.has(key)) this._precisionFormats.set(key,new Intl.NumberFormat(locale,{useGrouping:false,minimumFractionDigits:precision,maximumFractionDigits:precision,roundingMode:"halfEven"}));
      const formatter = this._precisionFormats.get(key);
      if (formatter.resolvedOptions().roundingMode !== "halfEven") return null;
      let text = formatter.format(!digits || length < -6 ? "0" : raw);
      if (/^-0(?:[,.]0+)?$/.test(text)) text = text.slice(1);
      return `${text} ${(unit || "").trim().replace(/\s+/g," ").slice(0,20)}`.trim().slice(0,40);
    } catch (_ignored) { return null; }
  }
  personPresenceText(card,state) {
    const meta=this.entityFor(card.entity_id)?.person_presence,raw=state?.state;
    if (typeof raw!=="string" || meta?.state!==[...raw].slice(0,256).join("")) return this.t("unknown");
    const language=(this._hass?.locale?.language || this._hass?.language || "en").replaceAll("_","-").split("-")[0].toLowerCase(),text=meta.text?.[language==="pl" ? "pl" : "en"];
    return typeof text==="string" && text.length>0 && [...text].length<=40 ? text : this.t("unknown");
  }
  calendarEventText(card,state) {
    const meta=this.entityFor(card.entity_id)?.calendar_next,attrs=state?.attributes,fields=meta?.fields,unknown=this.t("unknown"),keys=["message","all_day","start_time","end_time"];
    if (!["on","off"].includes(state?.state) || !attrs || !meta || meta.state!==state.state || !fields || typeof fields!=="object" || Array.isArray(fields) ||
      Object.keys(fields).some(key=>!keys.includes(key))) return unknown;
    for (const key of keys) {
      if (Object.hasOwn(attrs,key)!==Object.hasOwn(fields,key)) return unknown;
      if (Object.hasOwn(attrs,key)) {
        const value=key==="message" && typeof attrs[key]==="string" ? [...attrs[key]].slice(0,256).join("") : attrs[key];
        if (value!==fields[key]) return unknown;
      }
    }
    const polish=this._hass?.locale?.language?.startsWith("pl") || this._hass?.language?.startsWith("pl"),text=meta.text?.[polish ? "pl" : "en"];
    return typeof text==="string" && [...text].length<=40 ? text : unknown;
  }
  calendarDateText(raw) {
    if (raw === "unavailable") return this.t("offline");
    if (typeof raw !== "string" || raw.length !== 10 || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(raw)) return this.t("unknown");
    const year = Number(raw.slice(0,4)), month = Number(raw.slice(5,7)), day = Number(raw.slice(8,10));
    const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
    const days = [31,leap ? 29 : 28,31,30,31,30,31,31,30,31,30,31];
    if (year < 1 || month < 1 || month > 12 || day < 1 || day > days[month-1]) return this.t("unknown");
    const locale = this._hass?.locale?.language ?? this._hass?.language;
    const polish = typeof locale === "string" && /^pl(?:[-_]|$)/i.test(locale);
    return polish ? `${raw.slice(8,10)}.${raw.slice(5,7)}.${raw.slice(0,4)}` : raw;
  }
  datetimeHelperText(state) {
    const raw = state?.state, attributes = state?.attributes, unknown = this.t("unknown");
    if (raw === "unavailable") return this.t("offline");
    if (typeof raw !== "string" || typeof attributes?.has_date !== "boolean" || typeof attributes?.has_time !== "boolean" || (!attributes.has_date && !attributes.has_time)) return unknown;
    let date = "", clock = raw;
    if (attributes.has_date) {
      if (raw.length !== (attributes.has_time ? 19 : 10) || (attributes.has_time && raw[10] !== " ")) return unknown;
      date = this.calendarDateText(raw.slice(0,10)); if (date === unknown) return unknown;
      clock = raw.slice(11);
    }
    if (attributes.has_time && (!/^[0-9]{2}:[0-9]{2}:[0-9]{2}$/.test(clock) || clock.length !== 8 || Number(clock.slice(0,2)) > 23 || Number(clock.slice(3,5)) > 59 || Number(clock.slice(6)) > 59)) return unknown;
    return attributes.has_date && attributes.has_time ? `${date} ${clock}` : attributes.has_date ? date : clock;
  }
  stateText(card) {
    if(this.isStatisticsAction(card)) return this.t(this.statisticsAvailability(card).ready?"statisticsControl":"statisticsUnavailable");
    if(this.isAgendaAction(card)) return this.t(this.agendaAvailability(card).ready?"agendaControl":"agendaUnavailable");
    if(this.isTextPanelAction(card)) return this.textPanelPreview(card).message;
    if(this.isDatetimePanelAction(card)) return this.datetimePanelPreview(card).message;
    if (this.isExtraPanelAction(card)) {
      const preview=this.extraPreview(card);
      if (!preview.observation || preview.meta.panel_type==="lock") return preview.message;
      // Launcher captions keep existing labels, precision and calendar formatting.
      // The Inspector separately presents the full admitted Extra observation.
    }
    if (this.validCameraPreview(card)) return this.t(this.cameraPreviewAvailability(card)?"cameraCaptionOpen":"cameraCaptionUnavailable");
    if (this.isTileEventPanel(card)) return this.t("actionPanelOpen");
    if (card?.action?.kind === "event") return this.t("tileEvent");
    if (!card?.entity_id) return this.t("noEntity");
    const state = this._hass?.states?.[card.entity_id], entity = this.entityFor(card.entity_id);
    if (this.isPersonCard(card) && !state) return this.t("offline");
    if(card.entity_id.startsWith("media_player.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="repeat") {
      if(!state || state.state==="unavailable") return this.t("offline");
      const observed=this.observedMediaRepeat(card);
      if(!observed) return this.t("unknown");
      const locale=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl")?"pl":"en",caption=entity?.media_repeat?.captions?.[locale];
      if(typeof caption==="string" && caption.length>0 && [...caption].length<=40) return caption;
      let text;
      try {text=this._hass.formatEntityAttributeValue(state,"repeat");} catch {}
      if(typeof text!=="string" || !text.trim() || text===state.attributes.repeat) text=this.t({off:"repeatOff",one:"repeatOne",all:"repeatAll"}[state.attributes.repeat]);
      return this.t("mediaRepeatPrefix")+text;
    }
    if(card.entity_id.startsWith("media_player.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="source") {
      if(!state || state.state==="unavailable") return this.t("offline");
      const observed=this.observedMediaSource(card);
      if(!observed) return this.t("unknown");
      const locale=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl")?"pl":"en",caption=entity?.media_source?.captions?.[locale];
      if(typeof caption==="string" && caption.length>0 && [...caption].length<=40) return caption;
      try {const text=this._hass.formatEntityAttributeValue(state,"source");if(typeof text==="string" && text.trim())return text;} catch {}
      return observed.options[observed.index];
    }
    if(card.entity_id.startsWith("media_player.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="sound_mode") {
      if(!state || state.state==="unavailable") return this.t("offline");
      const observed=this.observedMediaSound(card);
      if(!observed) return this.t("unknown");
      const locale=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl")?"pl":"en",caption=entity?.media_sound_mode?.captions?.[locale];
      if(typeof caption==="string" && caption.length>0 && [...caption].length<=40) return caption;
      try {const text=this._hass.formatEntityAttributeValue(state,"sound_mode");if(typeof text==="string" && text.trim())return this.t("mediaSoundPrefix")+text;} catch {}
      return this.t("mediaSoundPrefix")+observed.options[observed.index];
    }
    if(!state && card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && card.action.service==="media_player.media_stop") return this.t("offline");
    if(!state && card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && card.action.service==="media_player.volume_mute") return this.t("offline");
    if(!state && card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && card.action.service==="media_player.shuffle_set") return this.t("offline");
    if(!state && card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && ["media_player.volume_set","media_player.volume_up","media_player.volume_down"].includes(card.action.service)) return this.t("offline");
    if (!state) return entity?.state || this.t("unknown");
    if (state.state === "unavailable") return this.t("offline");
    if(card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && card.action.service==="media_player.media_stop") {
      if(state.state==="unknown") return this.t("unknown");
      const locale=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl")?"pl":"en",text=entity?.media_stop?.text?.[locale];
      if(this.observedMediaStop(card) && typeof text==="string" && text.length>0 && [...text].length<=40) return text;
      try {const value=this._hass.formatEntityState?.(state);if(typeof value==="string" && value.trim())return this.t("mediaStatePrefix")+value;} catch {}
      return this.t("mediaStatePrefix")+state.state;
    }
    if(card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && card.action.service==="media_player.volume_mute") {
      if(state.state==="off") {
        try {const text=this._hass.formatEntityState?.(state);if(typeof text==="string" && text.trim() && text!==state.state)return text;} catch {}
        return this.t("mediaOff");
      }
      const observed=this.observedMediaMute(card),meta=this.entityFor(card.entity_id)?.media_mute;
      const language=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl")?"pl":"en",text=meta?.text?.[language];
      return observed===null ? this.t("unknown") : typeof text==="string" && text.length>0 && [...text].length<=40 ? text : this.t(observed?"mediaMuted":"mediaSoundOn");
    }
    if(card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && ["media_player.volume_set","media_player.volume_up","media_player.volume_down"].includes(card.action.service)) {
      if(!state || state.state==="unavailable") return this.t("offline");
      if(state.state==="off") {
        try {const text=this._hass.formatEntityState?.(state);if(typeof text==="string" && text.trim() && text!==state.state)return text;} catch {}
        return this.t("mediaOff");
      }
      const absolute=card.action.service==="media_player.volume_set",observed=absolute?this.observedMediaVolumeTarget(card):this.observedMediaVolume(card),locale=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl")?"pl":"en",text=entity?.[absolute?"media_volume_target":"media_volume"]?.text?.[locale];
      return observed && typeof text==="string" && text.length>0 && [...text].length<=40 ? text : this.t("unknown");
    }
    if(card.entity_id.startsWith("media_player.") && card.action?.kind==="service" && card.action.service==="media_player.shuffle_set") {
      if(state.state==="off") {
        try {const text=this._hass.formatEntityState?.(state);if(typeof text==="string" && text.trim() && text!==state.state)return text;} catch {}
        return this.t("mediaOff");
      }
      const observed=this.observedMediaShuffle(card),meta=this.entityFor(card.entity_id)?.media_shuffle;
      const language=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl")?"pl":"en",text=meta?.text?.[language];
      return observed===null ? this.t("unknown") : typeof text==="string" && text.length>0 && [...text].length<=40 ? text : this.t(observed?"mediaShuffled":"mediaInOrder");
    }
    if (card.entity_id.startsWith("climate.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="preset_mode") {
      const observed=this.observedClimatePreset(card);
      if (!observed) return this.t("unknown");
      if (observed.empty) return this.t("presetNone");
      const value=observed.options[observed.index];
      if (typeof this._hass.formatEntityAttributeValue==="function") {
        try { const text=this._hass.formatEntityAttributeValue(state,"preset_mode");if(typeof text==="string" && text.trim() && text!==value) return text; } catch {}
      }
      const key={none:"presetNone",eco:"presetEco",comfort:"presetComfort",sleep:"presetSleep",away:"presetAway",home:"presetHome",boost:"presetBoost",activity:"presetActivity"}[value];
      return key ? this.t(key) : value;
    }
    if (card.entity_id.startsWith("climate.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="fan_mode") {
      const observed=this.observedClimateFan(card);
      if (!observed) return this.t("unknown");
      const value=observed.options[observed.index];
      if (typeof this._hass.formatEntityAttributeValue==="function") {
        try { const text=this._hass.formatEntityAttributeValue(state,"fan_mode");if(typeof text==="string" && text.trim() && text!==value) return text; } catch {}
      }
      const key={auto:"airflowAuto",low:"airflowLow",medium:"airflowMedium",high:"airflowHigh",on:"airflowOn",off:"airflowOff",top:"airflowTop",middle:"airflowMiddle",focus:"airflowFocus",diffuse:"airflowDiffuse"}[value];
      return key ? this.t(key) : value;
    }
    if (card.entity_id.startsWith("climate.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="swing_mode") {
      const observed=this.observedClimateSwing(card);
      if (!observed) return this.t("unknown");
      const value=observed.options[observed.index];
      if (typeof this._hass.formatEntityAttributeValue==="function") {
        try { const text=this._hass.formatEntityAttributeValue(state,"swing_mode");if(typeof text==="string" && text.trim() && text!==value) return text; } catch {}
      }
      const key={off:"swingOff",on:"swingOn",vertical:"swingVertical",horizontal:"swingHorizontal",both:"swingBoth"}[value];
      return key ? this.t(key) : value;
    }
    if (card.entity_id.startsWith("climate.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="swing_horizontal_mode") {
      const observed=this.observedClimateHorizontal(card);
      if (!observed) return this.t("unknown");
      const value=observed.options[observed.index];
      if (typeof this._hass.formatEntityAttributeValue==="function") {
        try { const text=this._hass.formatEntityAttributeValue(state,"swing_horizontal_mode");if(typeof text==="string" && text.trim() && text!==value) return text; } catch {}
      }
      const key={off:"horizontalOff",on:"horizontalOn"}[value];
      return key ? this.t(key) : value;
    }
    if (card.entity_id.startsWith("light.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="effect") {
      const observed=this.observedLightEffect(card);
      if (!observed) return this.t("unknown");
      if (observed.empty) return this.t("effectEmpty");
      const value=observed.options[observed.index];
      if (typeof this._hass.formatEntityAttributeValue==="function") {
        try {const text=this._hass.formatEntityAttributeValue(state,"effect");if(typeof text==="string" && text.trim() && text!==value)return text;} catch {}
      }
      return value;
    }
    if (card.entity_id.startsWith("humidifier.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="mode") {
      const observed=this.observedHumidifierMode(card);
      if (!observed) return this.t("unknown");
      const value=observed.options[observed.index];
      if (typeof this._hass.formatEntityAttributeValue==="function") {
        try { const text=this._hass.formatEntityAttributeValue(state,"mode");if(typeof text==="string" && text.trim() && text!==value) return text; } catch {}
      }
      const key={normal:"humiModeNormal",eco:"humiModeEco",away:"humiModeAway",boost:"humiModeBoost",comfort:"humiModeComfort",home:"humiModeHome",sleep:"humiModeSleep",auto:"humiModeAuto",baby:"humiModeBaby"}[value];
      return key ? this.t(key) : value;
    }
    if (card.entity_id.startsWith("climate.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="hvac_mode") {
      if (!this.observedHVAC(card)) return this.t("unknown");
      if (typeof this._hass.formatEntityState==="function") {
        try { const text=this._hass.formatEntityState(state);if (typeof text==="string" && text.trim() && text!==state.state) return text; } catch {}
      }
      return this.t({off:"hvacOff",heat:"hvacHeat",cool:"hvacCool",heat_cool:"hvacHeatCool",auto:"hvacAuto",dry:"hvacDry",fan_only:"hvacFanOnly"}[state.state]);
    }
    if (card.entity_id.startsWith("humidifier.") && ["on","off"].includes(state.state) && !(card.action?.kind==="control" && card.action.control==="number" && card.action.property==="humidity")) {
      if (typeof this._hass.formatEntityState==="function") {
        try {const text=this._hass.formatEntityState(state);if(typeof text==="string" && text.trim() && text!==state.state)return text;} catch {}
      }
      return this.t(state.state==="on" ? "humidifierOn" : "humidifierOff");
    }
    if (card.entity_id.startsWith("input_text.") && state.state !== "unknown" && state.attributes?.mode !== "text") return this.t("hiddenText");
    if (this.stateLabelsEligible(card) && !["unknown","unavailable"].includes(state.state) && Object.hasOwn(card.state_labels || {},state.state)) return card.state_labels[state.state];
    // A momentary Action launcher opens its view; its timestamp remains in the Inspector.
    if (this.isActionPanelAction(card) && ["button","input_button","scene"].includes(this.actionPanelDomain(card)) && typeof state.state==="string") return this.t("actionPanelOpen");
    if (card.action?.kind === "fan_oscillation") {
      const value=this.fanOscillationValue(card);
      return value===null ? this.t("unknown") : this.t(value ? "fanOscillationOn" : "fanOscillationOff");
    }
    if (card.entity_id.startsWith("fan.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="direction") {
      const value=state.attributes?.direction,features=state.attributes?.supported_features;
      return ["on","off"].includes(state.state) && Number.isSafeInteger(features) && features>=0 && (features & 4) && ["forward","reverse"].includes(value) ? this.t(value==="forward" ? "directionForward" : "directionReverse") : this.t("unknown");
    }
    if (card.entity_id.startsWith("cover.") && card.action?.kind==="control" && card.action.control==="number" && card.action.property==="tilt_position") {
      const observed=this.observedCoverTilt(card);
      return observed ? this.t("coverTiltValue")+" "+observed.value+" %" : this.t("unknown");
    }
    if (card.entity_id.startsWith("cover.") && card.action?.kind==="control" && card.action.control==="number" && card.action.property==="position") {
      const observed=this.observedCoverPosition(card);
      return observed ? this.t("coverOpening")+" "+observed.value+" %" : this.t("unknown");
    }
    if (card.entity_id.startsWith("vacuum.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="fan_speed") {
      const observed=this.observedVacuumPower(card);
      if (!observed) return this.t("unknown");
      const value=observed.options[observed.index];
      if (typeof this._hass.formatEntityAttributeValue==="function") {
        try {const text=this._hass.formatEntityAttributeValue(state,"fan_speed");if(typeof text==="string" && text.trim() && text!==value)return text;} catch {}
      }
      return this.vacuumPowerLabel(value,observed.options);
    }
    if (card.entity_id.startsWith("fan.") && card.action?.kind==="control" && card.action.control==="choice" && card.action.property==="percentage") {
      const observed=this.observedFanSpeed(card);
      return observed ? observed.value+" %" : this.t("unknown");
    }
    if (card.entity_id.startsWith("light.") && card.action?.kind==="control" && card.action.control==="number" && card.action.property==="color_temp_kelvin") {
      const observed=this.observedColorTemperature(card);
      return observed ? observed.value+" K" : this.t("unknown");
    }
    if ((card.entity_id.startsWith("humidifier.") || card.entity_id.startsWith("climate.")) && card.action?.kind==="control" && card.action.control==="number" && card.action.property==="humidity") {
      const observed=this.observedHumidity(card);
      return observed ? this.t("temperatureTarget")+" "+observed.value+" %" : this.t("unknown");
    }
    if (card.entity_id.startsWith("climate.") && card.action?.kind==="control" && card.action.control==="number" && card.action.property==="temperature") {
      let observed=this.observedTemperature(card);
      if (!observed && this.climateTemperatureAvailability(card).caps?.readOnly) {
        const value=state.attributes?.temperature;
        if (typeof value==="number" && Number.isFinite(value)) observed={value,unit:this._hass.config.unit_system.temperature};
      }
      if (!observed) return this.t("unknown");
      return this.t("temperatureTarget")+" "+new Intl.NumberFormat(this._hass.locale?.language || this._hass.language || "en",{maximumFractionDigits:6}).format(observed.value)+" "+observed.unit;
    }
    if (card.entity_id.startsWith("fan.") && card.action?.kind === "control" && card.action.control === "choice") {
      const attrs=state.attributes, value=attrs?.preset_mode, options=attrs?.preset_modes;
      const empty=Object.hasOwn(attrs || {},"preset_mode") && value===null;
      return ["on","off"].includes(state.state) && Number.isSafeInteger(attrs?.supported_features) && attrs.supported_features>=0 && (attrs.supported_features & 8) &&
        Array.isArray(options) && options.length>=1 && options.length<=8 && new Set(options).size===options.length &&
        options.every(option=>typeof option==="string" && option.length>0 && !["unknown","unavailable"].includes(option) && new TextEncoder().encode(option).length<=32 && [...option].every(char=>char===" " || !/[\p{C}\p{Z}]/u.test(char))) && (options.includes(value) || empty) ? (empty ? this.t("fanManual") : value) : this.t("unknown");
    }
    if (card.type !== "sensor" && card.entity_id.startsWith("automation.") && ["on","off"].includes(state.state)) {
      const service = card.action?.kind === "default" ? (state.state === "on" ? "automation.turn_off" : "automation.turn_on") : card.action?.kind === "service" ? card.action.service : null;
      const label = this.automationServiceKey(service); if (label) return this.t(label);
    }
    if (card.entity_id.startsWith("input_text.") && !["unknown","unavailable"].includes(state.state)) return [...state.state.split(/[\p{White_Space}\u001c-\u001f]+/u).filter(Boolean).join(" ")].slice(0,40).join("");
    if (card.entity_id.startsWith("sensor.") && state.attributes?.device_class === "date") return this.calendarDateText(state.state);
    if (card.entity_id.startsWith("calendar.")) return this.calendarEventText(card,state);
    if (card.entity_id.startsWith("person.")) return this.personPresenceText(card,state);
    if (card.entity_id.startsWith("lawn_mower.")) {
      if (!["docked","paused","mowing","returning","error"].includes(state.state)) return this.t("unknown");
      const polish=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl");
      if (typeof this._hass.formatEntityState==="function") {
        try {
          const label=this._hass.formatEntityState(state),fallback=({error:["Error","Błąd"],returning:["Returning","Powrót"]})[state.state];
          if(typeof label==="string" && label.trim() && label!==state.state) return polish && fallback && label===fallback[0] && !this._hass.entities?.[card.entity_id]?.translation_key ? fallback[1] : label;
        } catch {}
      }
      return ({docked:["W bazie","Docked"],paused:["Pauza","Paused"],mowing:["Koszenie","Mowing"],returning:["Powrót","Returning"],error:["Błąd","Error"]})[state.state][polish?0:1];
    }
    if (card.entity_id.startsWith("vacuum.")) {
      if (!["cleaning","docked","idle","paused","returning","error"].includes(state.state)) return this.t("unknown");
      const polish=(this._hass.locale?.language || this._hass.language || "en").replaceAll("_","-").toLowerCase().startsWith("pl");
      if (typeof this._hass.formatEntityState==="function") {
        try {
          const label=this._hass.formatEntityState(state),fallback=({error:["Error","Błąd"],returning:["Returning","Powrót"]})[state.state];
          if (polish && state.state==="returning" && label==="wraca do stacji dokującej" && !this._hass.entities?.[card.entity_id]?.translation_key) return "Powrót do bazy";
          if(typeof label==="string" && label.trim() && label!==state.state) return polish && fallback && label===fallback[0] && !this._hass.entities?.[card.entity_id]?.translation_key ? fallback[1] : label;
        } catch {}
      }
      return ({docked:["W bazie","Docked"],paused:["Pauza","Paused"],cleaning:["Sprzątanie","Cleaning"],idle:["Bezczynny","Idle"],returning:["Powrót","Returning"],error:["Błąd","Error"]})[state.state][polish?0:1];
    }
    if (card.entity_id.startsWith("input_datetime.")) return this.datetimeHelperText(state);
    const duration=this.durationStateText(card,state);if(duration!==null) return duration;
    const precise = this.precisionStateText(card,state); if (precise !== null) return precise;
    if (typeof this._hass.formatEntityState === "function") {
      try {
        const translated = this._hass.formatEntityState(state);
        const polish = this._hass?.locale?.language?.startsWith("pl") || this._hass?.language?.startsWith("pl");
        if (polish && card.entity_id.startsWith("binary_sensor.") && state.attributes?.device_class === "presence" &&
            ["on","off"].includes(state.state) && ["Home","Away"].includes(translated) && !this._hass.entities?.[card.entity_id]?.translation_key) {
          return this.t(state.state === "on" ? "presencePresent" : "presenceAway");
        }
        return translated;
      } catch (_ignored) { /* Older HA frontends retain the raw fallback. */ }
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
      const colors = this.paletteColors(this.effectivePalette(card));
      node.style.setProperty("--tile-bg",colors.background); node.style.setProperty("--tile-fg",colors.foreground);
    }
    for (const node of this.shadowRoot.querySelectorAll(".palette-swatches [data-palette]")) node.style.background = this.paletteColors(node.dataset.palette).background;
  }
  observedMediaStop(card) {
    const state=this._hass?.states?.[card?.entity_id],features=state?.attributes?.supported_features,meta=this.entityFor(card?.entity_id)?.media_stop;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","off","standby","idle","playing","paused","buffering"].includes(state?.state) ||
      !Number.isSafeInteger(features) || features<0 || !(features&4096) || meta?.state!==state.state || meta.features!==features ||
      meta.eligible!==["playing","paused","buffering"].includes(state.state)) return null;
    return {state:state.state,eligible:meta.eligible};
  }
  mediaStopReady(card=this.cardAt(this._selectedSlot)) {
    const entity=this.entityFor(card?.entity_id),place=this.slotAt(card?.slot),descriptor=entity?.actions?.find(action=>action.service==="media_player.media_stop");
    return this.isConnected && !this._busy && !this._pending && !this._conflict && !this._drag && !this._carry && !Object.keys(this._fieldErrors).length && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_media_stop===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      ["entity","action"].includes(card?.type) && card.visible===true && place?.editable===true && place.hidden!==true && entity?.domain==="media_player" && entity.available===true &&
      this.observedMediaStop(card)!==null && descriptor?.fields && !Array.isArray(descriptor.fields) && Object.keys(descriptor.fields).length===0;
  }
  configureMediaStop() {
    const card=this.cardAt(this._selectedSlot);if(!this.mediaStopReady(card)) return false;
    const scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:"media_player.media_stop",data:{}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll)) pane.scrollTop=scroll;
    if(changed) pane?.querySelector('[data-action="media-stop-configure"]')?.focus({preventScroll:true});
    return changed;
  }
  observedMediaVolumeTarget(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.media_volume_target,features=attrs?.supported_features,value=attrs?.volume_level;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","idle","playing","paused","buffering"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features&4) ||
      typeof value!=="number" || !Number.isFinite(value) || value<0 || value>1 || meta?.state!==state.state || meta.features!==features || meta.value!==value) return null;
    return {value};
  }
  mediaVolumeTargetReady(card=this.cardAt(this._selectedSlot)) {
    const entity=this.entityFor(card?.entity_id),place=this.slotAt(card?.slot),fields=entity?.actions?.find(action=>action.service==="media_player.volume_set")?.fields,field=fields?.volume_level;
    return this.isConnected && !this._busy && !this._pending && !this._conflict && !this._drag && !this._carry && !Object.keys(this._fieldErrors).length && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_media_volume_target===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      ["entity","action"].includes(card?.type) && card.visible===true && place?.editable===true && place.hidden!==true && entity?.domain==="media_player" && entity.available===true &&
      this.observedMediaVolumeTarget(card)!==null && fields && !Array.isArray(fields) && Object.keys(fields).length===1 && field?.type==="number" && field.min===0 && field.max===1 && field.required===true;
  }
  configureMediaVolumeTarget() {
    const card=this.cardAt(this._selectedSlot);if(!this.mediaVolumeTargetReady(card))return false;
    const target=this.observedMediaVolumeTarget(card).value,scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:"media_player.volume_set",data:{volume_level:target}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll))pane.scrollTop=scroll;
    if(changed)pane?.querySelector('[data-field="data:volume_level"]')?.focus({preventScroll:true});
    return changed;
  }
  observedMediaVolume(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.media_volume,features=attrs?.supported_features,value=attrs?.volume_level,operations=meta?.operations;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","idle","playing","paused","buffering"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features&1028) ||
      typeof value!=="number" || !Number.isFinite(value) || value<0 || value>1 || meta?.state!==state.state || meta.features!==features || meta.value!==value ||
      !Array.isArray(operations) || !operations.length || operations.length>2 || new Set(operations).size!==operations.length || !operations.every(operation=>["volume_up","volume_down"].includes(operation))) return null;
    return {value,operations:[...operations]};
  }
  mediaVolumeReady(card=this.cardAt(this._selectedSlot),operation) {
    const entity=this.entityFor(card?.entity_id),place=this.slotAt(card?.slot),observed=this.observedMediaVolume(card),descriptor=entity?.actions?.find(action=>action.service===`media_player.${operation}`);
    return ["volume_up","volume_down"].includes(operation) && this.isConnected && !this._busy && !this._pending && !this._conflict && !this._drag && !this._carry && !Object.keys(this._fieldErrors).length && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_media_volume_actions===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      ["entity","action"].includes(card?.type) && card.visible===true && place?.editable===true && place.hidden!==true && entity?.domain==="media_player" && entity.available===true &&
      observed?.operations.includes(operation) && descriptor?.fields && Object.keys(descriptor.fields).length===0;
  }
  configureMediaVolume(operation) {
    const card=this.cardAt(this._selectedSlot);if(!this.mediaVolumeReady(card,operation)) return false;
    const scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:`media_player.${operation}`,data:{}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll)) pane.scrollTop=scroll;
    if(changed) pane?.querySelector(`[data-action="media-volume-configure"][data-operation="${operation}"]`)?.focus({preventScroll:true});
    return changed;
  }
  observedMediaMute(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.media_mute,features=attrs?.supported_features;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","idle","playing","paused","buffering"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features&8) ||
      typeof attrs?.is_volume_muted!=="boolean" || meta?.state!==state.state || meta.features!==features || meta.value!==attrs.is_volume_muted) return null;
    return attrs.is_volume_muted;
  }
  mediaMuteReady(card=this.cardAt(this._selectedSlot)) {
    const entity=this.entityFor(card?.entity_id),place=this.slotAt(card?.slot),field=entity?.actions?.find(action=>action.service==="media_player.volume_mute")?.fields?.is_volume_muted;
    return this.isConnected && !this._busy && !this._pending && !this._conflict && !this._drag && !this._carry && !Object.keys(this._fieldErrors).length && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_media_mute===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      ["entity","action"].includes(card?.type) && card.visible===true && place?.editable===true && place.hidden!==true && entity?.domain==="media_player" && entity.available===true && this.observedMediaMute(card)!==null && field?.type==="boolean" && field.required===true;
  }
  configureMediaMute(muted) {
    const card=this.cardAt(this._selectedSlot);if(typeof muted!=="boolean" || !this.mediaMuteReady(card)) return false;
    const scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:"media_player.volume_mute",data:{is_volume_muted:muted}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll)) pane.scrollTop=scroll;
    if(changed) pane?.querySelector(`[data-action="media-mute-configure"][data-muted="${muted}"]`)?.focus({preventScroll:true});
    return changed;
  }
  observedMediaShuffle(card) {
    const state=this._hass?.states?.[card?.entity_id],attrs=state?.attributes,meta=this.entityFor(card?.entity_id)?.media_shuffle,features=attrs?.supported_features;
    if(!card?.entity_id?.startsWith("media_player.") || !["on","idle","playing","paused","buffering"].includes(state?.state) || !Number.isSafeInteger(features) || features<0 || !(features&32768) ||
      typeof attrs?.shuffle!=="boolean" || meta?.state!==state.state || meta.features!==features || meta.value!==attrs.shuffle) return null;
    return attrs.shuffle;
  }
  mediaShuffleReady(card=this.cardAt(this._selectedSlot)) {
    const entity=this.entityFor(card?.entity_id),place=this.slotAt(card?.slot),field=entity?.actions?.find(action=>action.service==="media_player.shuffle_set")?.fields?.shuffle;
    return this.isConnected && !this._busy && !this._pending && !this._conflict && !this._drag && !this._carry && !Object.keys(this._fieldErrors).length && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_media_shuffle===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      ["entity","action"].includes(card?.type) && card.visible===true && place?.editable===true && place.hidden!==true && entity?.domain==="media_player" && entity.available===true && this.observedMediaShuffle(card)!==null && field?.type==="boolean" && field.required===true;
  }
  configureMediaShuffle(shuffled) {
    const card=this.cardAt(this._selectedSlot);if(typeof shuffled!=="boolean" || !this.mediaShuffleReady(card)) return false;
    const scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:"media_player.shuffle_set",data:{shuffle:shuffled}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll)) pane.scrollTop=scroll;
    if(changed) pane?.querySelector(`[data-action="media-shuffle-configure"][data-shuffled="${shuffled}"]`)?.focus({preventScroll:true});
    return changed;
  }
  remotePowerReady(card,operation) {
    const state=this._hass?.states?.[card?.entity_id],entity=this.entityFor(card?.entity_id),meta=entity?.remote_power,place=this.slotAt(card?.slot);
    return ["turn_on","turn_off"].includes(operation) && this.isConnected && !this._busy && !this._pending && !this._conflict && !this._drag && !this._carry && !Object.keys(this._fieldErrors).length && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_remote_power===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      card?.entity_id?.startsWith("remote.") && ["entity","action"].includes(card.type) && card.visible===true && place?.editable===true && place.hidden!==true &&
      ["on","off"].includes(state?.state) && entity?.available===true && meta?.state===state.state && Array.isArray(meta.supported) && meta.supported.includes(operation) &&
      Array.isArray(entity.actions) && entity.actions.some(action=>action.service===`remote.${operation}`);
  }
  configureRemotePower(operation) {
    const card=this.cardAt(this._selectedSlot);if(!this.remotePowerReady(card,operation)) return false;
    const scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:`remote.${operation}`,data:{}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll)) pane.scrollTop=scroll;
    if(changed) pane?.querySelector(`[data-action="remote-configure"][data-operation="${operation}"]`)?.focus({preventScroll:true});
    return changed;
  }
  mowerOperationReady(card,operation) {
    const features={start_mowing:1,pause:2,dock:4},state=this._hass?.states?.[card?.entity_id],entity=this.entityFor(card?.entity_id),meta=entity?.mower_actions,place=this.slotAt(card?.slot),flags=state?.attributes?.supported_features;
    return Object.hasOwn(features,operation) && this.isConnected && !this._busy && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_mower_actions===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      card?.entity_id?.startsWith("lawn_mower.") && ["entity","action"].includes(card.type) && card.visible===true && place?.editable===true && place.hidden!==true &&
      ["docked","paused","mowing","returning","error"].includes(state?.state) && Number.isSafeInteger(flags) && flags>=0 && !!(flags & features[operation]) &&
      entity?.available===true && meta?.state===state.state && meta.features===flags && Array.isArray(meta.supported) && meta.supported.includes(operation) &&
      Array.isArray(entity.actions) && entity.actions.some(action=>action.service===`lawn_mower.${operation}`);
  }
  configureMowerAction(operation) {
    const card=this.cardAt(this._selectedSlot);if (!this.mowerOperationReady(card,operation)) return false;
    this.finishField();return this.mutate(()=>{card.action={kind:"service",service:`lawn_mower.${operation}`,data:{}};});
  }
  vacuumOperationReady(card,operation) {
    const features={start:8192,pause:4,stop:8,return_to_base:16,locate:512,clean_spot:1024},state=this._hass?.states?.[card?.entity_id],entity=this.entityFor(card?.entity_id),meta=entity?.vacuum_actions,place=this.slotAt(card?.slot),flags=state?.attributes?.supported_features;
    return Object.hasOwn(features,operation) && this.isConnected && !this._busy && !this._pending && !this._conflict && !this._drag && !this._carry && !Object.keys(this._fieldErrors).length && !this._profileStale && !this._statusError && this._hass?.connected!==false &&
      this.profile?.schema_vacuum_actions===true && this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      card?.entity_id?.startsWith("vacuum.") && ["entity","action"].includes(card.type) && card.visible===true && place?.editable===true && place.hidden!==true &&
      ["cleaning","docked","idle","paused","returning","error"].includes(state?.state) && Number.isSafeInteger(flags) && flags>=0 && !!(flags & features[operation]) &&
      entity?.available===true && meta?.state===state.state && meta.features===flags && Array.isArray(meta.supported) && meta.supported.includes(operation) &&
      Array.isArray(entity.actions) && entity.actions.some(action=>action.service===`vacuum.${operation}`);
  }
  configureVacuumAction(operation) {
    const card=this.cardAt(this._selectedSlot);if (!this.vacuumOperationReady(card,operation)) return false;
    const scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:`vacuum.${operation}`,data:{}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll)) pane.scrollTop=scroll;
    if(changed) pane?.querySelector(`[data-action="vacuum-configure"][data-operation="${operation}"]`)?.focus({preventScroll:true});
    return changed;
  }
  vacuumAreas(card=this.cardAt(this._selectedSlot)) {
    const state=this._hass?.states?.[card?.entity_id],entity=this.entityFor(card?.entity_id),meta=entity?.vacuum_area,flags=state?.attributes?.supported_features,place=this.slotAt(card?.slot);
    const descriptor=entity?.actions?.find(item=>item.service==="vacuum.clean_area")?.fields?.cleaning_area_id;
    if (!this.isConnected || this._busy || this._pending || this._conflict || this._drag || this._carry || this._profileStale || this._statusError || Object.keys(this._fieldErrors).length || this._hass?.connected===false ||
        this.profile?.schema_vacuum_area!==true || this._status?.device_available!==true || this._status.context_press_version!==1 || this._status.press_enabled_version!==1 ||
        !card?.entity_id?.startsWith("vacuum.") || !["entity","action"].includes(card.type) || card.visible!==true || place?.editable!==true || place.hidden===true ||
        !["cleaning","docked","idle","paused","returning","error"].includes(state?.state) || !Number.isSafeInteger(flags) || flags<0 || !(flags & 16384) ||
        entity?.available!==true || meta?.state!==state.state || meta.features!==flags || !Array.isArray(meta.areas) || meta.areas.length<1 || meta.areas.length>32 ||
        !meta.areas.every(area=>typeof area?.id==="string" && area.id.length>0 && area.id.length<=128 && typeof area.name==="string" && area.name.length<=80) ||
        new Set(meta.areas.map(area=>area.id)).size!==meta.areas.length || descriptor?.type!=="select" || descriptor.required!==true ||
        JSON.stringify(descriptor.options)!==JSON.stringify(meta.areas.map(area=>area.id))) return [];
    return meta.areas;
  }
  configureVacuumArea(areaId) {
    const card=this.cardAt(this._selectedSlot);if (!this.vacuumAreas(card).some(area=>area.id===areaId)) { this.paintInspector(); return false; }
    const scroll=this.shadowRoot.querySelector("#inspector")?.scrollTop;
    this.finishField();const changed=this.mutate(()=>{card.action={kind:"service",service:"vacuum.clean_area",data:{cleaning_area_id:areaId}};});
    const pane=this.shadowRoot.querySelector("#inspector");if(pane && Number.isFinite(scroll)) pane.scrollTop=scroll;
    if(changed) pane?.querySelector('[data-field="vacuum-area"]')?.focus({preventScroll:true});
    return changed;
  }
  stateColorEligible(card) {
    const domain = card?.entity_id?.split(".")[0];
    return (card?.type === "entity" && ["light","switch","input_boolean","fan","humidifier"].includes(domain)) || (["entity","action"].includes(card?.type) && domain === "automation") || (card?.type === "sensor" && ["binary_sensor","person"].includes(domain));
  }
  serviceLabel(service) {
    const key=this.automationServiceKey(service) || ({"media_player.volume_set":"mediaVolumeTarget","media_player.media_stop":"mediaStop","media_player.volume_up":"mediaLouder","media_player.volume_down":"mediaQuieter","media_player.shuffle_set":"mediaShuffleService","media_player.repeat_set":"mediaRepeatControl","media_player.select_source":"mediaSourceControl","media_player.select_sound_mode":"mediaSoundControl","media_player.volume_mute":"mediaMuteService","remote.turn_on":"remoteOn","remote.turn_off":"remoteOff","lawn_mower.start_mowing":"mowerStart","lawn_mower.pause":"mowerPause","lawn_mower.dock":"mowerDock","vacuum.clean_area":"vacuumRoom","vacuum.start":"vacuumStart","vacuum.pause":"vacuumPause","vacuum.stop":"vacuumStop","vacuum.return_to_base":"vacuumDock","vacuum.locate":"vacuumLocate","vacuum.clean_spot":"vacuumSpot"})[service];
    return key ? this.t(key) : service;
  }
  automationServiceKey(service) { return ({"automation.turn_on":"automationEnable","automation.turn_off":"automationDisable","automation.trigger":"automationRun"})[service]; }
  autoIconEligible(card) { return card?.type === "sensor" && card.entity_id?.startsWith("binary_sensor."); }
  effectiveIcon(card) {
    if (card?.icon !== "auto") return card?.icon || "sensor";
    const deviceClass = this._hass?.states?.[card.entity_id]?.attributes?.device_class;
    if (["door","window","opening","garage_door"].includes(deviceClass)) return "door";
    if (["motion","occupancy","presence"].includes(deviceClass)) return "presence";
    if (deviceClass === "moisture") return "humidity";
    return "sensor";
  }
  humidifierPowerReady(card) {
    const state=this._hass?.states?.[card?.entity_id],entity=this.entityFor(card?.entity_id);
    if (!card?.entity_id?.startsWith("humidifier.") || !["on","off"].includes(state?.state) || this.profile?.schema_humidifier_power!==true ||
      this._profileStale || this._hass?.connected===false || this._status?.device_available!==true || this._status.context_press_version!==1 || this._status.press_enabled_version!==1 ||
      entity?.available!==true) return false;
    const operation=state.state==="on" ? "turn_off" : "turn_on";
    return Array.isArray(entity.actions) && entity.actions.some(action=>action.service===`humidifier.${operation}`);
  }
  fanOscillationValue(card) {
    const state=this._hass?.states?.[card?.entity_id], attributes=state?.attributes;
    return card?.entity_id?.startsWith("fan.") && ["on","off"].includes(state?.state) &&
      Number.isSafeInteger(attributes?.supported_features) && attributes.supported_features>=0 && (attributes.supported_features & 2) &&
      typeof attributes.oscillating==="boolean" ? attributes.oscillating : null;
  }
  fanOscillationReady(card) {
    const entity=this.entityFor(card?.entity_id), slot=this.slotAt(card?.slot);
    return !this._profileStale && this._hass?.connected!==false && this.profile?.schema_fan_oscillation===true &&
      Array.isArray(this.profile.layout_versions) && this.profile.layout_versions.includes(3) && card?.type!=="sensor" && card?.visible===true && slot?.editable && !slot.hidden &&
      this._status?.device_available===true && this._status.context_press_version===1 && this._status.press_enabled_version===1 &&
      this.fanOscillationValue(card)!==null && typeof entity?.fan_oscillation?.value==="boolean" &&
      entity?.available===true && Array.isArray(entity?.actions) && entity.actions.some(action=>action.service==="fan.oscillate");
  }
  effectivePalette(card) {
    if (card?.state_color === true && this.stateColorEligible(card)) {
      const state = this._hass?.states ? this._hass.states[card.entity_id]?.state : this.entityFor(card.entity_id)?.state;
      if (this.isPersonCard(card) ? state!=="home" : card.action?.kind === "fan_oscillation" ? this.fanOscillationValue(card) !== true : state !== "on") return "surface";
    }
    return card?.palette || "surface";
  }
  hex(value) { return `#${(Number(value)&0xFFFFFF).toString(16).padStart(6,"0")}`; }
  pageTitle(page) { return page.id === "home-2" ? this.t("security") : page.id === "home-4" ? this.t("controls") : page.id === "home-5" ? this.carouselText("Narzędzia","Tools") : page.title; }
  carouselText(pl,en) { return this._hass?.locale?.language?.startsWith("pl") || this._hass?.language?.startsWith("pl") ? pl : en; }
  carouselOrder() { return this._draft?.home_order || this.profile?.carousel_order || [...(this.profile?.pages || [])].sort((a,b) => a.order-b.order).map(page => page.id); }
  editCarousel(action,pageId) {
    if (!this.profile?.carousel_order?.includes(pageId) || pageId === "home-1" || this._saving || this._conflict) return;
    const order = [...this.carouselOrder()];
    const at = order.indexOf(pageId);
    if (action === "carousel-toggle") {
      if (pageId === "home-3") return;
      if (at < 0) order.push(pageId);
      else order.splice(at,1);
    } else {
      const next = at + (action === "carousel-up" ? -1 : 1);
      if (at < 1 || next < 1 || next >= order.length) return;
      [order[at],order[next]] = [order[next],order[at]];
    }
    if (this.mutate(layout => { layout.home_order = order; })) {
      const panel = this.shadowRoot.querySelector("#carousel-pages");
      if (panel) panel.open = true;
      panel?.querySelector(`[data-action="${action}"][data-page="${pageId}"]:not(:disabled)`)?.focus();
    }
  }
  carouselMarkup() {
    if (!this.profile?.carousel_order) return "";
    const order = this.carouselOrder();
    const pages = [...order,...this.profile.carousel_order.filter(id => !order.includes(id))];
    const up = this.carouselText("Przenieś wcześniej","Move earlier");
    const down = this.carouselText("Przenieś później","Move later");
    return `<details id="carousel-pages"><summary>${this.carouselText("Kolejność i widoczność stron","Page order and visibility")}</summary>
      <ol>${pages.map(id => {
        const page = this.profile.pages.find(item => item.id === id), at = order.indexOf(id);
        const title = AEH_ESCAPE(id === "home-1" ? this.t("home") : id === "home-3" ? this.t("apps") : this.pageTitle(page));
        return `<li><span>${title}</span>
          <button data-action="carousel-up" data-page="${id}" aria-label="${up} · ${title}" ${at < 2 ? "disabled" : ""}>${this.icon("mdi:arrow-up")}</button>
          <button data-action="carousel-down" data-page="${id}" aria-label="${down} · ${title}" ${at < 1 || at >= order.length-1 ? "disabled" : ""}>${this.icon("mdi:arrow-down")}</button>
          <button data-action="carousel-toggle" data-page="${id}" ${id === "home-1" || id === "home-3" ? "disabled" : ""}>${at < 0 ? this.carouselText("Pokaż","Show") : this.carouselText("Ukryj","Hide")}</button>
        </li>`;
      }).join("")}</ol></details>`;
  }
  pageMarkup() {
    if (!Array.isArray(this.profile?.pages)) return "";
    const editable = new Set(this.pages.map(page => page.id));
    const order = this.carouselOrder();
    const rank = page => order.includes(page.id) ? order.indexOf(page.id) : order.length + page.order;
    return [...this.profile.pages].sort((a,b) => rank(a)-rank(b)).map(page => {
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
      const card = this.cardAt(slot.slot), colors = this.paletteColors(this.effectivePalette(card));
      const shape = slot.radius ?? Math.min(slot.width,slot.height)/2;
      const compact = slot.height <= 120, strip = slot.height < 90, sensor = slot.slot === 13 || slot.slot === 14;
      const style = `left:${slot.x/8}%;top:${slot.y/8}%;width:${slot.width/8}%;height:${slot.height/8}%;--tile-bg:${colors.background};--tile-fg:${colors.foreground};border-radius:${shape/8}cqw;`;
      return `<div class="preview-card ${card ? "" : "empty-card"} ${card && !card.visible ? "hidden-card" : ""} ${(selecting ? this._selectedCardIds.has(card?.id) : this._selectedSlot === slot.slot) ? "selected" : ""} ${compact ? "compact" : ""} ${strip ? "strip" : ""} ${sensor ? "data-card" : ""}" style="${style}" data-slot="${slot.slot}" data-action="slot" role="button" tabindex="${selecting && !card ? -1 : 0}" ${selecting && !card ? 'aria-disabled="true"' : ""} aria-label="${AEH_ESCAPE(card?.title || this.t("emptySlot"))}, ${this.t("slot")} ${slot.slot+1}" aria-pressed="${selecting ? this._selectedCardIds.has(card?.id) : this._selectedSlot === slot.slot}">
        ${card ? `<div class="tile-content">${sensor ? "" : this.icon(this.effectiveIcon(card),'class="tile-icon"')}<span class="tile-title">${AEH_ESCAPE(card.title)}</span><span class="tile-state" data-live-slot="${slot.slot}">${AEH_ESCAPE(this.stateText(card))}</span></div>${selecting ? "" : `<button class="tile-drag" data-drag-kind="card" data-from="${slot.slot}" title="${this.t("drag")}" aria-label="${this.t("drag")} ${AEH_ESCAPE(card.title)}">${this.icon("mdi:drag")}</button>`}${!card.visible ? `<span class="hidden-badge">${this.t("hidden")}</span>` : ""}` : `<span class="empty-plus">+</span><span class="empty-label">${this.t("empty")}</span>`}
      </div>`;
    }).join("");
    return `<div class="screen" role="group" aria-label="${AEH_ESCAPE(page ? this.pageTitle(page) : this.t("preview"))}"><div class="screen-chrome">${this.icon("mdi:volume-high")}${this.icon("mdi:wifi")}</div><div class="screen-title">${AEH_ESCAPE(page ? this.pageTitle(page) : "")}</div>${cards}<div class="screen-dots">${this.carouselOrder().map(id => `<i class="${id === this._pageId ? "current" : ""}"></i>`).join("")}</div></div>`;
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
  libraryState(entity) {
    if (entity.entity_id.startsWith("input_text.") && this._hass?.states?.[entity.entity_id]?.attributes?.mode !== "text") return {state:this.t("hiddenText"),available:false};
    if (!this._hass?.states) return {state:entity.state,available:entity.available !== false};
    const state = this._hass.states[entity.entity_id]?.state;
    return {state:typeof state === "string" ? state : "unavailable",available:typeof state === "string" && state !== "unknown" && state !== "unavailable"};
  }
  libraryMarkup() {
    if (this._catalogueError) return `<p class="inline-error">${AEH_ESCAPE(this._catalogueError)}</p><button data-action="retry">${this.t("retry")}</button>`;
    return `<p class="library-count">${this._catalogueTotal ?? this._catalogue.length} ${this.t("matches")}${this._truncated ? ` · ${this.t("more")}` : ""}</p>${this._areasTruncated ? `<p class="hint">${this.t("areaLimit")}</p>` : ""}<div class="entity-list">${this._catalogue.map(entity => `<div class="entity-row"><button class="entity-main" data-action="entity" data-entity="${AEH_ESCAPE(entity.entity_id)}" title="${this.t("add")}"><span class="entity-icon">${this.icon(({camera:"camera",person:"presence",calendar:"clock",sun:"clock",light:"light",climate:"climate",cover:"cover",lock:"lock",alarm_control_panel:"alarm",fan:"fan",scene:"scene",switch:"switch"})[entity.domain] || "action")}</span><span class="entity-copy"><strong>${AEH_ESCAPE(entity.name)}</strong><small>${AEH_ESCAPE(entity.entity_id)}</small></span><span data-live-entity-state="${AEH_ESCAPE(entity.entity_id)}" class="entity-state${this.libraryState(entity).available ? "" : " unavailable"}">${AEH_ESCAPE(this.libraryState(entity).state)}</span></button><button class="entity-drag" data-drag-kind="entity" data-entity="${AEH_ESCAPE(entity.entity_id)}" title="${this.t("drag")}" aria-label="${this.t("drag")} ${AEH_ESCAPE(entity.name)}">${this.icon("mdi:drag")}</button></div>`).join("") || `<p class="empty-library">${this.t("noEntities")}</p>`}</div>`;
  }
  fieldMarkup(key,descriptor,value) {
    if(key==="volume_level" && this.cardAt(this._selectedSlot)?.action?.service==="media_player.volume_set" && descriptor.type==="number") {
      const percent=typeof value==="number" && Number.isFinite(value)?Number((value*100).toPrecision(15)):"";
      return `<label>${this.t("mediaVolumePercent")}<input type="number" data-field="data:volume_level" aria-label="${this.t("mediaVolumePercent")}" min="0" max="100" step="any" required value="${AEH_ESCAPE(percent)}"></label>`;
    }
    const attributes = `data-field="data:${AEH_ESCAPE(key)}" ${["is_volume_muted","shuffle"].includes(key)?`aria-label="${this.t(key==="shuffle"?"mediaShuffleField":"mediaMuteField")}"`:""} ${descriptor.required ? "required" : ""}`;
    let control;
    if (descriptor.type === "select" || descriptor.type === "boolean") {
      const values = descriptor.type === "boolean" ? [{value:"true",label:this.t("true")},{value:"false",label:this.t("false")}] : descriptor.options.map((option,index) => ({value:option,label:descriptor.option_labels?.[index] || option}));
      control = `<select ${attributes}><option value="">${this.t(descriptor.required ? "required" : "optional")}</option>${values.map(option => `<option value="${AEH_ESCAPE(option.value)}" ${String(value) === String(option.value) ? "selected" : ""}>${AEH_ESCAPE(option.label)}</option>`).join("")}</select>`;
    } else if (descriptor.type === "number") control = `<input type="number" ${attributes} ${descriptor.min === undefined ? "" : `min="${descriptor.min}"`} ${descriptor.max === undefined ? "" : `max="${descriptor.max}"`} step="${descriptor.step ?? "any"}" value="${AEH_ESCAPE(value ?? "")}" placeholder="${this.t(descriptor.required ? "required" : "optional")}">`;
    else control = `<input type="text" ${attributes} value="${AEH_ESCAPE(Array.isArray(value) ? value.join(", ") : value ?? "")}" placeholder="${this.t("rgb")}">`;
    const label = ({shuffle:"mediaShuffleField",repeat:"mediaRepeatControl",is_volume_muted:"mediaMuteField",cleaning_area_id:"vacuumRoom",duration:"timerDuration",skip_condition:"skipConditions",stop_actions:"stopActions"})[key];
    return `<label>${label ? this.t(label) : AEH_ESCAPE(key.replaceAll("_"," "))}${control}</label>`;
  }
  inspectorMarkup() {
    if (this._selectingCards) return `<div class="empty-inspector"><h2>${this.t("multiActive")}</h2><p>${this.t("multiHint")}</p><p>${this.t("multiKeyboard")}</p></div>`;
    const slot = this.slotAt(this._selectedSlot), card = this.cardAt(this._selectedSlot);
    if (!slot) return `<div class="inspector-placeholder">${this.icon("mdi:cursor-default-click-outline")}<h2>${this.t("inspector")}</h2><p>${this.t("selectCard")}</p></div>`;
    const header = `<div class="inspector-heading"><span class="eyebrow">${this.t("slot")} ${slot.slot+1}</span><button class="icon-button" data-action="close-inspector" aria-label="${this.t("close")}">${this.icon("mdi:close")}</button></div>`;
    if (!card) return `${header}<h2>${this.t("empty")}</h2><p>${this.t("changeEntity")}</p>${this.pasteMarkup(slot.slot)}<button class="text-button" data-action="focus-library">${this.icon("mdi:magnify")}${this.t("search")}</button>${this.tileEventPanelAvailability(slot.slot) ? `<button class="text-button" data-action="create-tile-event-panel">${this.icon("action")}${this.t("tileEventPanelCreate")}</button>` : ""}${this.eventAvailability(slot.slot) ? `<button class="text-button" data-action="create-tile-event">${this.icon("action")}${this.t("tileEventCreate")}</button>` : ""}`;
    const options = (values,selected) => values.map(value => `<option value="${AEH_ESCAPE(value)}" ${value === selected ? "selected" : ""}>${value === "auto" ? this.t("autoIcon") : AEH_ESCAPE(value.replaceAll("_"," "))}</option>`).join("");
    const entity = this.entityFor(card.entity_id), actions = entity?.actions || [], action = actions.find(item => item.service === card.action.service);
    const controlKind = this.cardControlKind(card);
    const lightControl = this.controlAvailability(card,controlKind), savedControl = card.action.kind === "control" && (this.isStatisticsAction(card) || this.isAgendaAction(card) || this.isTextPanelAction(card) || this.isDatetimePanelAction(card) || this.isActionPanelAction(card) || this.isActionParametersAction(card) || this.isMediaPanelAction(card) || this.isExtraPanelAction(card) || controlKind==="lightdetail" && card.action.control==="light" && card.action.detail===1 || controlKind==="climatepanel" && card.action.control==="panel" && card.action.property==="climate" || card.action.control === "panel" && card.action.property===this.panelFamily(card) || card.action.control === (controlKind === "humiditypanel" ? "humidifier" : controlKind) && !card.action.property);
    const extraActionParameters=controlKind!=="actionparameterspanel" && this.actionParametersAvailability(card).ready ? `<option value="control-actionparameterspanel">${this.t("actionParametersControl")}</option>` : "";
    const extraLegacyAction=this.isActionParametersAction(card) && this.actionPanelAvailability(card).ready ? `<option value="control-actionpanel">${this.t("actionPanelControl")}</option>` : "";
    const extraStatistics=controlKind!=="statisticspanel" && this.statisticsAvailability(card).ready ? `<option value="control-statisticspanel">${this.t("statisticsControl")}</option>` : "";
    const extraInfo=this.isStatisticsAction(card) && this.extraPanelAvailability(card,"info").ready ? `<option value="control-infopanel">${this.controlText("control","infopanel")}</option>` : "";
    const extraAgenda=controlKind!=="agendapanel" && this.agendaAvailability(card).ready ? `<option value="control-agendapanel">${this.t("agendaControl")}</option>` : "";
    const extraMediaPanel=controlKind!=="mediapanel" && this.mediaPanelAvailability(card).ready ? `<option value="control-mediapanel">${this.t("mediaPanelControl")}</option>` : "";
    const controlOption = !["remoteactivity","mediasource","mediarepeat","mediasound"].includes(controlKind) && (lightControl.ready || savedControl) ? `<option value="${["textpanel","datetimepanel","actionpanel","actionparameterspanel","mediapanel","agendapanel","statisticspanel","infopanel","lockpanel","lightdetail","climatepanel","timerpanel","remotepanel","powerpanel"].includes(controlKind) ? "control-"+controlKind : controlKind === "number" ? "control-number" : controlKind === "choice" ? "control-choice" : controlKind === "cover" ? "control-cover" : controlKind === "fan" ? "control-fan" : controlKind === "humiditypanel" ? "control-humiditypanel" : controlKind === "robot" ? "control-robot" : "control"}" ${savedControl ? "selected" : ""} ${lightControl.ready ? "" : "disabled"}>${this.controlText("control",controlKind)}</option>` : "";
    const extraLightDetail=controlKind!=="lightdetail" && this.detailControlAvailability(card,"light").ready ? `<option value="control-lightdetail">${this.t("lightDetailControl")}</option>` : "";
    const detailFacetsHint=savedControl && ["lightdetail","climatepanel"].includes(controlKind) && lightControl.missingFacets?.length ? `<p class="hint">${this.t("detailFacetUnavailable")}</p>` : "";
    const savedPreset=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="preset_mode", preset=this.climatePresetAvailability(card);
    const presetOption=preset.ready || savedPreset ? `<option value="control-preset" ${savedPreset ? "selected" : ""} ${preset.ready ? "" : "disabled"}>${this.t("presetControl")}</option>` : "";
    const presetHint=savedPreset ? `<p class="hint" data-climate-preset>${this.t(preset.reason)}</p>` : "";
    const savedAirflow=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="fan_mode", airflow=this.climateFanAvailability(card);
    const airflowOption=airflow.ready || savedAirflow ? `<option value="control-airflow" ${savedAirflow ? "selected" : ""} ${airflow.ready ? "" : "disabled"}>${this.t("airflowControl")}</option>` : "";
    const airflowHint=savedAirflow ? `<p class="hint" data-climate-airflow>${this.t(airflow.reason)}</p>` : "";
    const savedSwing=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="swing_mode", swing=this.climateSwingAvailability(card);
    const swingOption=swing.ready || savedSwing ? `<option value="control-swing" ${savedSwing ? "selected" : ""} ${swing.ready ? "" : "disabled"}>${this.t("swingControl")}</option>` : "";
    const swingHint=savedSwing ? `<p class="hint" data-climate-swing>${this.t(swing.reason)}</p>` : "";
    const savedHorizontal=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="swing_horizontal_mode", horizontal=this.climateHorizontalAvailability(card);
    const horizontalOption=horizontal.ready || savedHorizontal ? `<option value="control-horizontal" ${savedHorizontal ? "selected" : ""} ${horizontal.ready ? "" : "disabled"}>${this.t("horizontalControl")}</option>` : "";
    const horizontalHint=savedHorizontal ? `<p class="hint" data-climate-horizontal>${this.t(horizontal.reason)}</p>` : "";
    const savedHumiMode=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="mode", humiMode=this.humidifierModeAvailability(card);
    const humiModeOption=humiMode.ready || savedHumiMode ? `<option value="control-humidifier" ${savedHumiMode ? "selected" : ""} ${humiMode.ready ? "" : "disabled"}>${this.t("humiModeControl")}</option>` : "";
    const humiModeHint=savedHumiMode ? `<p class="hint" data-humidifier-mode>${this.t(humiMode.reason)}</p>` : "";
    const savedHVAC=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="hvac_mode", hvac=this.climateHVACAvailability(card);
    const hvacOption=hvac.ready || savedHVAC ? `<option value="control-hvac" ${savedHVAC ? "selected" : ""} ${hvac.ready ? "" : "disabled"}>${this.t("hvacControl")}</option>` : "";
    const hvacHint=savedHVAC ? `<p class="hint" data-climate-hvac>${this.t(hvac.reason)}</p>` : "";
    const savedEffect=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="effect", effect=this.lightEffectAvailability(card);
    const effectOption=effect.ready || savedEffect ? `<option value="control-effect" ${savedEffect ? "selected" : ""} ${effect.ready ? "" : "disabled"}>${this.t("effectControl")}</option>` : "";
    const effectHint=savedEffect ? `<p class="hint" data-light-effect>${this.t(effect.reason)}</p>` : "";
    const savedCoverTilt=card.entity_id.startsWith("cover.") && card.action.kind==="control" && card.action.control==="number" && card.action.property==="tilt_position", coverTilt=this.coverTiltAvailability(card);
    const coverTiltOption=coverTilt.ready || savedCoverTilt ? `<option value="control-covertilt" ${savedCoverTilt ? "selected" : ""} ${coverTilt.ready ? "" : "disabled"}>${this.t("coverTiltControl")}</option>` : "";
    const coverTiltHint=savedCoverTilt ? `<p class="hint" data-cover-tilt>${this.t(coverTilt.reason)}</p>` : "";
    const savedCoverPosition=card.entity_id.startsWith("cover.") && card.action.kind==="control" && card.action.control==="number" && card.action.property==="position", coverPosition=this.coverPositionAvailability(card);
    const coverPositionOption=coverPosition.ready || savedCoverPosition ? `<option value="control-coverposition" ${savedCoverPosition ? "selected" : ""} ${coverPosition.ready ? "" : "disabled"}>${this.t("coverPositionControl")}</option>` : "";
    const coverPositionHint=savedCoverPosition ? `<p class="hint" data-cover-position>${this.t(coverPosition.reason)}</p>` : "";
    const savedMediaRepeat=card.entity_id.startsWith("media_player.") && card.action.kind==="control" && card.action.control==="choice" && card.action.property==="repeat", mediaRepeat=this.mediaRepeatAvailability(card);
    const mediaRepeatOption=mediaRepeat.ready || savedMediaRepeat ? `<option value="control-mediarepeat" ${savedMediaRepeat?"selected":""} ${mediaRepeat.ready?"":"disabled"}>${this.t("mediaRepeatControl")}</option>` : "";
    const mediaRepeatHint=savedMediaRepeat ? `<p class="hint" data-media-repeat>${this.t(mediaRepeat.reason)}</p>` : "";
    const savedMediaSource=card.entity_id.startsWith("media_player.") && card.action.kind==="control" && card.action.control==="choice" && card.action.property==="source", mediaSource=this.mediaSourceAvailability(card);
    const mediaSourceOption=mediaSource.ready || savedMediaSource ? `<option value="control-mediasource" ${savedMediaSource?"selected":""} ${mediaSource.ready?"":"disabled"}>${this.t("mediaSourceControl")}</option>` : "";
    const mediaSourceHint=savedMediaSource ? `<p class="hint" data-media-source>${this.t(mediaSource.reason)}</p>` : "";
    const savedMediaSound=card.entity_id.startsWith("media_player.") && card.action.kind==="control" && card.action.control==="choice" && card.action.property==="sound_mode", mediaSound=this.mediaSoundAvailability(card);
    const mediaSoundOption=mediaSound.ready || savedMediaSound ? `<option value="control-mediasound" ${savedMediaSound?"selected":""} ${mediaSound.ready?"":"disabled"}>${this.t("mediaSoundControl")}</option>` : "";
    const mediaSoundHint=savedMediaSound ? `<p class="hint" data-media-sound>${this.t(mediaSound.reason)}</p>` : "";
    const savedRemoteActivity=card.entity_id.startsWith("remote.") && card.action.kind==="control" && card.action.control==="choice" && card.action.property==="activity", activity=this.remoteActivityAvailability(card);
    const activityOption=activity.ready || savedRemoteActivity ? `<option value="control-remoteactivity" ${savedRemoteActivity?"selected":""} ${activity.ready?"":"disabled"}>${this.t("activityControl")}</option>` : "";
    const activityHint=savedRemoteActivity ? `<p class="hint" data-remote-activity>${this.t(activity.reason)}</p>` : "";
    const savedVacuumPower=card.entity_id.startsWith("vacuum.") && card.action.kind==="control" && card.action.control==="choice" && card.action.property==="fan_speed", vacuumPower=this.vacuumPowerAvailability(card);
    const vacuumPowerOption=vacuumPower.ready || savedVacuumPower ? `<option value="control-vacuumfan" ${savedVacuumPower ? "selected" : ""} ${vacuumPower.ready ? "" : "disabled"}>${this.t("vacuumPowerControl")}</option>` : "";
    const vacuumPowerHint=savedVacuumPower ? `<p class="hint" data-vacuum-power>${this.t(vacuumPower.reason)}</p>` : "";
    const savedSpeed=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="percentage", speed=this.fanSpeedAvailability(card);
    const speedOption=speed.ready || savedSpeed ? `<option value="control-speed" ${savedSpeed ? "selected" : ""} ${speed.ready ? "" : "disabled"}>${this.t("speedControl")}</option>` : "";
    const speedHint=savedSpeed ? `<p class="hint" data-fan-speed>${this.t(speed.reason)}</p>` : "";
    const savedKelvin=card.action.kind==="control" && card.action.control==="number" && card.action.property==="color_temp_kelvin", kelvin=this.lightColorTemperatureAvailability(card);
    const kelvinOption=kelvin.ready || savedKelvin ? `<option value="control-kelvin" ${savedKelvin ? "selected" : ""} ${kelvin.ready ? "" : "disabled"}>${this.t("kelvinControl")}</option>` : "";
    const kelvinHint=savedKelvin ? `<p class="hint" data-light-color-temperature>${this.t(kelvin.reason)}</p>` : "";
    const savedClimateHumidity=card.entity_id.startsWith("climate.") && card.action.kind==="control" && card.action.control==="number" && card.action.property==="humidity", climateHumidity=this.climateHumidityAvailability(card);
    const climateHumidityOption=climateHumidity.ready || savedClimateHumidity ? `<option value="control-climatehumidity" ${savedClimateHumidity ? "selected" : ""} ${climateHumidity.ready ? "" : "disabled"}>${this.t("climateHumidityControl")}</option>` : "";
    const climateHumidityHint=savedClimateHumidity ? `<p class="hint" data-climate-humidity>${this.t(climateHumidity.reason)}</p>` : "";
    const savedHumidity=card.entity_id.startsWith("humidifier.") && card.action.kind==="control" && card.action.control==="number" && card.action.property==="humidity", humidity=this.humidifierHumidityAvailability(card);
    const humidityOption=humidity.ready || savedHumidity ? `<option value="control-humidity" ${savedHumidity ? "selected" : ""} ${humidity.ready ? "" : "disabled"}>${this.t("humidityControl")}</option>` : "";
    const humidityHint=savedHumidity ? `<p class="hint" data-humidifier-humidity>${this.t(humidity.reason)}</p>` : "";
    const savedTemperature=card.action.kind==="control" && card.action.control==="number" && card.action.property==="temperature", temperature=this.climateTemperatureAvailability(card);
    const temperatureOption=temperature.ready || savedTemperature ? `<option value="control-temperature" ${savedTemperature ? "selected" : ""} ${temperature.ready ? "" : "disabled"}>${this.t("temperatureControl")}</option>` : "";
    const temperatureHint=savedTemperature ? `<p class="hint" data-climate-temperature>${this.t(temperature.reason)}</p>` : "";
    const savedDirection=card.action.kind==="control" && card.action.control==="choice" && card.action.property==="direction", direction=this.fanDirectionAvailability(card);
    const directionOption=direction.ready || savedDirection ? `<option value="control-direction" ${savedDirection ? "selected" : ""} ${direction.ready ? "" : "disabled"}>${this.t("directionControl")}</option>` : "";
    const directionHint=savedDirection ? `<p class="hint" data-fan-direction>${this.t(direction.reason)}</p>` : "";
    const savedOscillation=card.action.kind==="fan_oscillation", oscillationReady=this.fanOscillationReady(card);
    const oscillationOption=oscillationReady || savedOscillation ? `<option value="fan_oscillation" ${savedOscillation ? "selected" : ""} ${oscillationReady ? "" : "disabled"}>${this.t("fanOscillation")}</option>` : "";
    const oscillationHint=savedOscillation ? `<p class="hint" data-fan-oscillation>${this.t("fanOscillationHint")}</p>` : "";
    const savedCamera=this.validCameraPreview(card),cameraReady=this.cameraPreviewAvailability(card);
    const cameraOption=card.entity_id.startsWith("camera.") && card.type==="entity" ? `<option value="camera_preview" ${savedCamera?"selected":""} ${cameraReady?"":"disabled"}>${this.t("cameraPreview")}</option>`:"";
    const cameraHint=card.entity_id.startsWith("camera.") ? `<p class="hint">${this.t(cameraReady?"cameraPreviewHint":"cameraPreviewUnavailable")}</p>${savedCamera?`<button type="button" class="text-button" data-action="camera-preview-configure" ${cameraReady?"":"disabled"}>${this.t("cameraPreviewConfigure")} · ${card.action.duration_seconds} s</button>`:""}`:"";
    const savedEventPanel=this.isTileEventPanel(card), eventPanelReady=this.tileEventPanelAvailability(slot.slot);
    const eventPanelOption=eventPanelReady || savedEventPanel ? `<option value="tile-event-panel" ${savedEventPanel?"selected":""} ${eventPanelReady?"":"disabled"}>${this.t("tileEventPanel")}</option>`:"";
    const savedEvent = card.action.kind === "event", eventReady = this.eventAvailability(slot.slot);
    const eventOption = eventReady || savedEvent ? `<option value="event" ${savedEvent ? "selected" : ""} ${eventReady ? "" : "disabled"}>${this.t("tileEvent")}</option>` : "";
    const controlHint = !this.isStatisticsAction(card) && !savedRemoteActivity && !savedCoverTilt && !savedCoverPosition && !savedVacuumPower && !savedClimateHumidity && !savedSpeed && !savedKelvin && !savedEffect && !savedHumidity && !savedHumiMode && !savedHorizontal && !savedSwing && !savedAirflow && !savedPreset && !savedHVAC && !savedTemperature && !savedDirection && card.action.kind !== "fan_oscillation" && (savedControl || controlKind==="actionpanel" && ["entity","action"].includes(card.type) || this.extraPanelFamily(card) && card.type==="sensor" || (card.type === "entity" && (card.entity_id.startsWith("light.") || ["textpanel","datetimepanel","actionpanel","actionparameterspanel","mediapanel","agendapanel","statisticspanel","infopanel","lockpanel","lightdetail","climatepanel","timerpanel","remotepanel","powerpanel","number","choice","cover","fan","humiditypanel","robot"].includes(controlKind)))) ? `<p class="hint" data-light-control-hint>${this.t(lightControl.reason)}</p>` : "";
    const sunHint = this.isSunCard(card) && !this.isExtraPanelAction(card) ? `<p class="hint" data-sun-placement>${this.t("sunPlacement")}</p>` : "";
    const calendarHint=this.isStatisticsAction(card) ? `<p class="hint" data-statistics-panel>${this.t(lightControl.reason)}</p>` : this.isAgendaAction(card) ? `<p class="hint" data-agenda-panel>${this.t("agendaHint")}</p>` : this.isCalendarCard(card) ? `<p class="hint" data-calendar-next>${this.t("calendarHint")} ${this.t("calendarPlacement")}</p>` : "";
    const personHint=this.isPersonCard(card) && !this.isExtraPanelAction(card) ? `<p class="hint" data-person-presence>${this.t("personHint")} ${this.t("personPlacement")}</p>` : "";
    const vacuumAreas=this.vacuumAreas(card),selectedArea=card.action?.service==="vacuum.clean_area" ? card.action.data?.cleaning_area_id : "";
    const vacuumRoomHint=card.entity_id.startsWith("vacuum.") && card.type!=="sensor" ? `<div data-vacuum-room><label>${this.t("vacuumRoom")}<select data-field="vacuum-area" aria-label="${this.t("vacuumRoom")}" ${vacuumAreas.length?"":"disabled"}><option value="">${this.t("vacuumRoomChoose")}</option>${selectedArea && !vacuumAreas.some(area=>area.id===selectedArea)?`<option selected disabled value="${AEH_ESCAPE(selectedArea)}">${this.t("vacuumRoomUnavailable")}</option>`:""}${vacuumAreas.map(area=>`<option value="${AEH_ESCAPE(area.id)}" ${selectedArea===area.id?"selected":""}>${AEH_ESCAPE(area.name)}</option>`).join("")}</select></label><p class="hint">${this.t(vacuumAreas.length?"vacuumRoomHint":"vacuumRoomMissing")}</p><button type="button" class="text-button" data-action="vacuum-rooms-refresh">${this.t("vacuumRoomRefresh")}</button></div>` : "";
    const vacuumActionsHint=card.entity_id.startsWith("vacuum.") && card.type!=="sensor" ? `<div data-vacuum-actions><p class="hint">${this.t("vacuumActionsHint")}</p><div class="operation-options">${["start","pause","stop","return_to_base","locate","clean_spot"].map(operation=>`<button type="button" class="operation-option" data-action="vacuum-configure" data-operation="${operation}" aria-pressed="${card.action?.kind==="service" && card.action.service===`vacuum.${operation}`}" ${this.vacuumOperationReady(card,operation)?"":"disabled"}>${AEH_ESCAPE(this.serviceLabel(`vacuum.${operation}`))}</button>`).join("")}</div></div>` : "";
    const legacyMediaShortcuts=card.entity_id.startsWith("media_player.") && card.type!=="sensor" && !this.isMediaPanelAction(card);
    const mediaMuteHint=legacyMediaShortcuts && this.profile.schema_media_mute===true && (this.entityFor(card.entity_id)?.actions?.some(action=>action.service==="media_player.volume_mute") || card.action?.kind==="service" && card.action.service==="media_player.volume_mute") ? `<div data-media-mute><p class="hint">${this.t("mediaMuteHint")}</p><div class="operation-options">${[true,false].map(muted=>`<button type="button" class="operation-option" data-action="media-mute-configure" data-muted="${muted}" aria-pressed="${card.action?.kind==="service" && card.action.service==="media_player.volume_mute" && card.action.data?.is_volume_muted===muted}" ${this.mediaMuteReady(card)?"":"disabled"}>${this.t(muted?"mediaMute":"mediaUnmute")}</button>`).join("")}</div></div>` : "";
    const mediaVolumeTargetHint=legacyMediaShortcuts && this.profile.schema_media_volume_target===true && (this.entityFor(card.entity_id)?.actions?.some(action=>action.service==="media_player.volume_set") || card.action?.service==="media_player.volume_set") ? `<div data-media-volume-target><p class="hint">${this.t("mediaVolumeTargetHint")}</p><button type="button" class="operation-option" data-action="media-volume-target-configure" ${this.mediaVolumeTargetReady(card)?"":"disabled"}>${this.t("mediaVolumeTarget")}</button></div>` : "";
    const mediaStopHint=legacyMediaShortcuts && this.profile.schema_media_stop===true && (this.entityFor(card.entity_id)?.actions?.some(action=>action.service==="media_player.media_stop") || card.action?.kind==="service" && card.action.service==="media_player.media_stop") ? `<div data-media-stop><p class="hint">${this.t("mediaStopHint")}</p><div class="operation-options"><button type="button" class="operation-option" data-action="media-stop-configure" aria-pressed="${card.action?.kind==="service" && card.action.service==="media_player.media_stop"}" ${this.mediaStopReady(card)?"":"disabled"}>${this.t("mediaStop")}</button></div></div>` : "";
    const mediaVolumeHint=legacyMediaShortcuts && this.profile.schema_media_volume_actions===true && (this.entityFor(card.entity_id)?.actions?.some(action=>["media_player.volume_up","media_player.volume_down"].includes(action.service)) || card.action?.kind==="service" && ["media_player.volume_up","media_player.volume_down"].includes(card.action.service)) ? `<div data-media-volume><p class="hint">${this.t("mediaVolumeHint")}</p><div class="operation-options">${["volume_up","volume_down"].map(operation=>`<button type="button" class="operation-option" data-action="media-volume-configure" data-operation="${operation}" aria-pressed="${card.action?.kind==="service" && card.action.service===`media_player.${operation}`}" ${this.mediaVolumeReady(card,operation)?"":"disabled"}>${this.t(operation==="volume_up"?"mediaLouder":"mediaQuieter")}</button>`).join("")}</div></div>` : "";
    const mediaShuffleHint=legacyMediaShortcuts && this.profile.schema_media_shuffle===true && (this.entityFor(card.entity_id)?.actions?.some(action=>action.service==="media_player.shuffle_set") || card.action?.kind==="service" && card.action.service==="media_player.shuffle_set") ? `<div data-media-shuffle><p class="hint">${this.t("mediaShuffleHint")}</p><div class="operation-options">${[true,false].map(shuffled=>`<button type="button" class="operation-option" data-action="media-shuffle-configure" data-shuffled="${shuffled}" aria-pressed="${card.action?.kind==="service" && card.action.service==="media_player.shuffle_set" && card.action.data?.shuffle===shuffled}" ${this.mediaShuffleReady(card)?"":"disabled"}>${this.t(shuffled?"mediaShuffle":"mediaUnshuffle")}</button>`).join("")}</div></div>` : "";
    const remoteHint=card.entity_id.startsWith("remote.") && card.type!=="sensor" && !savedRemoteActivity ? `<div data-remote-power><p class="hint">${this.t("remoteHint")}</p><div class="operation-options">${["turn_on","turn_off"].map(operation=>`<button type="button" class="operation-option" data-action="remote-configure" data-operation="${operation}" aria-pressed="${card.action?.kind==="service" && card.action.service===`remote.${operation}`}" ${this.remotePowerReady(card,operation)?"":"disabled"}>${this.t(operation==="turn_on"?"remoteOn":"remoteOff")}</button>`).join("")}</div></div>` : "";
    const mowerHint=card.entity_id.startsWith("lawn_mower.") && card.type!=="sensor" ? `<div data-mower-actions><p class="hint">${this.t("mowerHint")}</p>${["start_mowing","pause","dock"].map(operation=>`<button type="button" class="text-button" data-action="mower-configure" data-operation="${operation}" aria-pressed="${card.action?.kind==="service" && card.action.service===`lawn_mower.${operation}`}" ${this.mowerOperationReady(card,operation)?"":"disabled"}>${this.t(({start_mowing:"mowerStart",pause:"mowerPause",dock:"mowerDock"})[operation])}</button>`).join("")}</div>` : "";
    const datetimeHint = this.isDatetimeCard(card) && !this.isDatetimePanelAction(card) ? `<p class="hint" data-datetime-placement>${this.t("datetimePlacement")}</p>` : "";
    const stateColorField = this.stateColorEligible(card) ? `<label class="switch-row"><span>${this.t("stateColor")}</span><input data-field="state_color" type="checkbox" ${card.state_color === true ? "checked" : ""}></label><p class="hint" data-state-color>${this.t("stateColorHint")}</p>` : "";
    const precisionField = this.precisionEligible(card) ? `<label>${this.t("precision")}<select data-field="display_precision"><option value="" ${card.display_precision === undefined ? "selected" : ""}>${this.t("precisionAuto")}</option>${[0,1,2,3,4,5,6].map(value=>`<option value="${value}" ${card.display_precision === value ? "selected" : ""}>${value}</option>`).join("")}</select></label><p class="hint" data-precision-hint>${this.t("precisionHint")}</p>` : "";
    const timerHint = card.action.kind === "service" && card.action.service === "timer.start" ? `<p class="hint" data-timer-duration>${this.t("timerDurationHint")}</p>` : "";
    const humidifierHint=card.entity_id.startsWith("humidifier.") && card.action.kind==="default" ? `<p class="hint" data-humidifier-power>${this.t(this.humidifierPowerReady(card) ? "humidifierPowerHint" : "humidifierPowerUnavailable")}</p>` : "";
    const automationHintKey = card.entity_id.startsWith("automation.") ? (card.action.kind === "default" ? "automationHint" : card.action.service === "automation.trigger" ? "automationRunHint" : card.action.service === "automation.turn_off" ? "automationOffHint" : null) : null;
    const automationHint = automationHintKey ? `<p class="hint" data-automation-hint>${this.t(automationHintKey)}</p>` : "";
    const actionNote = card.type === "sensor" || humidifierHint ? "" : savedEventPanel ? `<p class="hint" data-tile-event-panel-hint>${this.t(eventPanelReady?"tileEventPanelHint":"tileEventPanelUnavailable")}</p>` : savedEvent ? `<p class="hint" data-tile-event-hint>${this.t(eventReady ? "tileEventHint" : "tileEventUnavailable")}</p>` : savedCoverTilt || savedCoverPosition || savedVacuumPower || savedClimateHumidity || savedSpeed || savedKelvin || savedEffect || savedHumidity || savedHumiMode || savedHorizontal || savedSwing || savedAirflow || savedPreset || savedHVAC || savedTemperature || savedDirection || savedControl && ["textpanel","datetimepanel","actionpanel","actionparameterspanel","mediapanel","agendapanel","statisticspanel","infopanel","lockpanel","lightdetail","climatepanel","timerpanel","remotepanel","powerpanel","number","choice","cover","fan","humiditypanel","robot"].includes(controlKind) ? "" : `<p class="hint">${this.t(savedControl ? "controlHint" : "actionsNote")}</p>`;
    const panelDurationMarkup=savedControl && controlKind==="timerpanel" ? `<label>${this.t("panelDuration")}<input data-field="panel-duration" type="number" min="1" max="86400" step="1" value="${AEH_ESCAPE(card.action.initial_duration??"")}"></label><p class="hint">${this.t("panelDurationHint")}</p>` : "";
    const serviceMarkup = card.action.kind === "service" ? `<label>${this.t("service")}<select data-field="service" required><option value="">${this.t("chooseService")}</option>${actions.map(item => `<option value="${AEH_ESCAPE(item.service)}" ${card.action.service === item.service ? "selected" : ""}>${AEH_ESCAPE(this.serviceLabel(item.service))}</option>`).join("")}${card.action.service && !action ? `<option selected value="${AEH_ESCAPE(card.action.service)}">${AEH_ESCAPE(card.action.service)}</option>` : ""}</select></label>${!actions.length ? `<p class="hint">${this.t("noActions")}</p>` : ""}${card.action.service && !action ? `<p class="inline-error">${this.t("actionUnavailable")}</p>` : ""}${action ? Object.entries(action.fields || {}).filter(([key])=>key!=="cleaning_area_id").map(([key,descriptor]) => this.fieldMarkup(key,descriptor,card.action.data?.[key])).join("") : ""}` : "";
    return `${header}<h2>${AEH_ESCAPE(card.title || this.t("inspector"))}</h2><form id="properties" autocomplete="off">
      <section class="property-group">${savedEvent || savedEventPanel ? "" : `<label>${this.t("entity")}<span class="entity-reference">${AEH_ESCAPE(card.entity_id || this.t("noEntity"))}</span></label><button type="button" class="text-button" data-action="focus-library">${this.t("changeEntity")}</button>`}
      <label>${this.t("title")}<input data-field="title" value="${AEH_ESCAPE(card.title)}" maxlength="40"></label>
      <label>${this.t("type")}<select data-field="type">${["entity","sensor","action"].filter(type => slot.types.includes(type) && (!this.isRestrictedTextCard(card) || this.validExtraPanelAction(card) && type==="entity" || type === "sensor")).map(type => `<option value="${type}" ${card.type === type ? "selected" : ""}>${this.t(type+"Type")}</option>`).join("")}</select></label></section>
      <section class="property-group"><label>${this.t("icon")}<select data-field="icon">${options(this._data.icons.filter(icon=>icon!=="auto" || this.autoIconEligible(card)),card.icon)}</select></label><label>${this.t("palette")}<select data-field="palette">${options(this._data.palettes,card.palette)}</select></label><div class="palette-swatches">${this._data.palettes.map(palette => `<span data-palette="${AEH_ESCAPE(palette)}" style="background:${this.paletteColors(palette).background}" title="${AEH_ESCAPE(palette)}"></span>`).join("")}</div>${stateColorField}<label class="switch-row"><span>${this.t("visible")}</span><input data-field="visible" type="checkbox" ${card.visible ? "checked" : ""}></label></section>
      ${this.profile.schema_state_labels === true && this.stateLabelsEligible(card) ? `<button type="button" class="text-button" data-action="state-labels">${this.t("stateLabels")}</button>` : ""}${precisionField}<section class="property-group"><label>${this.t("tap")}<select data-field="action-kind" aria-label="${this.t("tap")}" ${this.sensorActionEditable(card) ? "" : "disabled"}>${(card.type==="sensor" || card.entity_id.startsWith("camera.")?["none"]:["default","none","service"]).map(kind => `<option value="${kind}" ${card.action.kind === kind ? "selected" : ""}>${this.t(kind)}</option>`).join("")}${controlOption}${extraActionParameters}${extraLegacyAction}${extraInfo}${extraAgenda}${extraStatistics}${extraMediaPanel}${extraLightDetail}${eventOption}${eventPanelOption}${cameraOption}${oscillationOption}${directionOption}${temperatureOption}${hvacOption}${presetOption}${airflowOption}${swingOption}${horizontalOption}${humiModeOption}${humidityOption}${effectOption}${kelvinOption}${speedOption}${climateHumidityOption}${mediaRepeatOption}${mediaSoundOption}${mediaSourceOption}${activityOption}${vacuumPowerOption}${coverPositionOption}${coverTiltOption}</select></label>${serviceMarkup}${this.isActionPanelAction(card)?this.actionPanelPolicyMarkup(card,undefined,true):""}${this.actionPanelPreviewMarkup(card)}${this.isActionParametersAction(card)?this.actionParametersPreviewMarkup(card):""}${cameraHint}${panelDurationMarkup}${timerHint}${automationHint}${humidifierHint}${oscillationHint}${directionHint}${temperatureHint}${hvacHint}${presetHint}${airflowHint}${swingHint}${horizontalHint}${humiModeHint}${humidityHint}${effectHint}${kelvinHint}${speedHint}${climateHumidityHint}${mediaRepeatHint}${mediaSoundHint}${mediaSourceHint}${activityHint}${vacuumPowerHint}${coverPositionHint}${coverTiltHint}${controlHint}${detailFacetsHint}${this.extraPanelPreviewMarkup(card)}${this.datetimePanelPreviewMarkup(card)}${this.textPanelPreviewMarkup(card)}${savedRemoteActivity || savedMediaSource || savedMediaRepeat || savedMediaSound?"":actionNote}${sunHint}${datetimeHint}${calendarHint}${personHint}${mediaVolumeTargetHint}${mediaStopHint}${mediaVolumeHint}${mediaShuffleHint}${mediaMuteHint}${remoteHint}${mowerHint}${vacuumActionsHint}${vacuumRoomHint}<p class="inline-error" data-field-error>${AEH_ESCAPE(Object.values(this._fieldErrors).join(" "))}</p></section>
      <section class="property-group"><label>${this.t("move")}<select id="move-target"><option value="">${this.t("choosePlace")}</option>${this.pages.map(page => `<optgroup label="${AEH_ESCAPE(this.pageTitle(page))}">${this.slots.filter(item => item.page_id === page.id && item.slot !== slot.slot && (!this.isRestrictedTextCard(card) || this.acceptsCard(item,card)) && (!this.isRestrictedTextCard(this.cardAt(item.slot)) || this.acceptsCard(slot,this.cardAt(item.slot)))).map(item => `<option value="${item.slot}">${this.t("slot")} ${item.slot+1} · ${AEH_ESCAPE(this.cardAt(item.slot)?.title || this.t("emptySlot"))}</option>`).join("")}</optgroup>`).join("")}</select></label><button class="text-button" type="button" data-action="copy-card" title="${this.t("copy")} (Ctrl/Cmd+C)">${this.icon("mdi:content-copy")}${this.t("copy")}</button><button class="text-button" type="button" data-action="cut-card" title="${this.t("cut")} (Ctrl/Cmd+X)">${this.icon("mdi:content-cut")}${this.t("cut")}</button><button class="danger text-button" type="button" data-action="remove">${this.icon("mdi:delete-outline")}${this.t("remove")}</button></section>
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
    return `<div id="device-identity">${this.deviceIdentityMarkup()}</div><p class="hint">${this.t("profileHint")}</p>${Array.isArray(profile.sun_text_slots) ? `<p class="hint" data-sun-capability>${this.t("sunPlacement")}</p>` : ""}${Array.isArray(profile.datetime_text_slots) ? `<p class="hint" data-datetime-capability>${this.t("datetimePlacement")}</p>` : ""}<dl class="capabilities-grid">${facts.map(([key,value]) => `<div><dt>${this.t(key)}</dt><dd>${AEH_ESCAPE(value)}</dd></div>`).join("")}${flags.map(([key,label]) => `<div><dt>${this.t(label)}</dt><dd>${this.t(profile.features?.[key] === true ? "supported" : profile.features?.[key] === false ? "notSupported" : "unknown")}</dd></div>`).join("")}</dl>`;
  }
  feedbackMarkup() {
    const conflict = this._restoreConflict ? this.dt("conflict").replace("{base}",this._draftBaseRevision).replace("{current}",this._saved.revision) : this.t("conflict");
    return `${this._conflict ? `<div class="conflict" role="alert">${this.icon("mdi:source-branch")}<span>${AEH_ESCAPE(conflict)}</span><button data-action="${this._restoreConflict ? "review-draft" : "reload"}">${this._restoreConflict ? this.dt("review") : this.t("reload")}</button></div>` : ""}${this._error ? `<p class="feedback error" role="alert">${AEH_ESCAPE(this._error)}</p>` : ""}${this._notice ? `<p class="feedback" role="status">${AEH_ESCAPE(this._notice)}${this._recovery ? ` <button class="text-button" data-action="restore">${this.t("restore")}</button>` : ""}</p>` : ""}${this._storageError ? `<p class="feedback">${this.dt("unavailable")}</p>` : ""}`;
  }
  modalMarkup() {
    if (!this._pending) return "";
    if (this._pending.kind === "state-labels") {
      const current = this.stateLabelsReviewCurrent(), invalid = this.labelsFromRows(this._pending.rows) === null;
      const rows = this._pending.rows.map((row,index)=>`<div class="state-label-row"><label>${this.t("stateLabelsKey")}<input data-label-index="${index}" data-label-part="key" value="${AEH_ESCAPE(row.key)}" ${!current ? "disabled" : ""}></label><label>${this.t("stateLabelsValue")}<input data-label-index="${index}" data-label-part="label" value="${AEH_ESCAPE(row.label)}" ${!current ? "disabled" : ""}></label><button data-action="state-label-remove" data-index="${index}" ${!current ? "disabled" : ""} aria-label="${this.t("stateLabelsRemove")}">${this.icon("mdi:delete-outline")}</button></div>`).join("");
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><h2 id="modal-title">${this.t("stateLabels")}</h2><p>${this.t("stateLabelsHint")}</p><div class="state-label-rows">${rows}</div><button class="text-button" data-action="state-label-add" ${!current || this._pending.rows.length >= 8 ? "disabled" : ""}>${this.t("stateLabelsAdd")}</button><p class="inline-error" data-labels-error>${!current ? this.t("stateLabelsChanged") : invalid ? this.t("stateLabelsInvalid") : ""}</p><div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="primary" data-action="modal-state-labels" ${this._busy || !current || invalid ? "disabled" : ""}>${this.t("stateLabelsApply")}</button></div></section></div>`;
    }
    if (this._pending.kind === "camera-preview") {
      const card=this.cardAt(this._pending.slot),current=this.cameraPreviewReviewCurrent();
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><span class="modal-symbol">${this.icon("camera")}</span><h2 id="modal-title">${this.t("cameraPreviewReview")}</h2><p>${this.t("cameraPreviewHint")}</p><div class="import-summary">${AEH_ESCAPE(card?.title)}<br>${AEH_ESCAPE(card?.entity_id)}</div><label>${this.t("cameraPreviewDuration")}<input type="number" min="15" max="90" step="1" data-camera-duration value="${this._pending.duration??""}" ${current?"":"disabled"}></label><p class="hint">15–90 s</p><div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="primary" data-action="modal-camera-preview" ${this._busy || !current || !this.cameraPreviewDurationValid()?"disabled":""}>${this.t("cameraPreviewConfirm")}</button></div></section></div>`;
    }
    if (this._pending.kind === "tile-event") {
      const card = this.cardAt(this._pending.slot);
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><span class="modal-symbol">${this.icon("action")}</span><h2 id="modal-title">${this.t(this._pending.panel?"tileEventPanelReview":"tileEventReview")}</h2><p>${this.t(card ? "tileEventReviewHint" : "tileEventEmptyHint")}</p><div class="import-summary">${AEH_ESCAPE(card?.title || this.t("tileEvent"))}<br>${AEH_ESCAPE(card?.entity_id || "")}</div><p class="hint">${this.t(this._pending.panel?"tileEventPanelHint":"tileEventHint")}</p><div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="primary" data-action="modal-tile-event" ${this._busy || !this.tileEventReviewCurrent() ? "disabled" : ""}>${this.t(this._pending.panel?"tileEventPanelConfirm":"tileEventConfirm")}</button></div></section></div>`;
    }
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
      return `<div class="modal-shade"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><span class="modal-symbol">${this.icon(controlKind==="statisticspanel" ? "mdi:chart-line" : controlKind==="agendapanel" ? "mdi:calendar-month" : controlKind==="textpanel" ? "mdi:form-textbox" : controlKind==="datetimepanel" ? "clock" : ["temperature","humidity","hvac","preset","airflow","swing","horizontal","humidifier"].includes(controlKind) ? "climate" : controlKind === "number" ? "mdi:numeric" : controlKind === "cover" ? "cover" : controlKind === "fan" ? "fan" : controlKind === "humiditypanel" ? "mdi:air-humidifier" : ["actionpanel","actionparameterspanel"].includes(controlKind) ? this.actionPanelIcon(card) : controlKind === "mediapanel" ? (this.entityFor(card?.entity_id)?.media_panel?.caps?.device_type==="tv"?"mdi:television":"mdi:speaker") : controlKind === "robot" ? (card?.entity_id?.startsWith("lawn_mower.") ? "mower" : "vacuum") : ["infopanel","lockpanel"].includes(controlKind) ? this.extraPanelIcon(card) : controlKind==="climatepanel" ? "mdi:thermostat" : controlKind==="timerpanel" ? "mdi:timer-outline" : controlKind==="remotepanel" ? "mdi:remote" : controlKind==="powerpanel" ? "mdi:power" : "light")}</span><h2 id="modal-title">${this.controlText("controlReviewTitle",controlKind)}</h2><p>${this.controlText(this._draft.version === 2 ? "controlReviewV2" : "controlReviewV3",controlKind)}</p><div class="import-summary">${AEH_ESCAPE(card?.title)}<br>${AEH_ESCAPE(card?.entity_id)}</div><p class="hint">${this.t(this.controlAvailability(card,controlKind).reason)}</p>${controlKind==="actionparameterspanel"?this.actionParametersPreviewMarkup(card):""}${controlKind==="actionpanel"?this.actionPanelPolicyMarkup(card,this._pending.actionPolicies):""}${controlKind==="actionpanel" && this.actionPanelDomain(card)==="script"?`<p class="hint">${this.t("actionPanelNoParameters")}</p>`:""}<div class="modal-actions"><button data-action="modal-cancel">${this.t("cancel")}</button><button class="primary" data-action="modal-light-control" ${this._busy || !this.lightControlReviewCurrent() ? "disabled" : ""}>${this.controlText("controlConfirm",controlKind)}</button></div></section></div>`;
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
      <section class="workspace"><div class="workspace-tools"><div><span class="eyebrow">${this.t("preview")}</span><h2>${this.t("fixed")}</h2></div><div class="history-actions"><button class="icon-button" data-action="undo" aria-label="${this.t("undo")}" title="${this.t("undo")} (Ctrl+Z)">${this.icon("mdi:undo")}</button><button class="icon-button" data-action="redo" aria-label="${this.t("redo")}" title="${this.t("redo")} (Ctrl+Shift+Z)">${this.icon("mdi:redo")}</button></div></div><div id="card-selection">${this.cardSelectionMarkup()}</div><div id="card-clipboard">${this.clipboardMarkup()}</div><nav class="page-tabs" id="page-tabs" role="tablist">${this.pageMarkup()}</nav>${this.carouselMarkup()}<div class="device-stage" id="device-preview">${this.previewMarkup()}</div><p class="preview-caption">${this.t("previewHint")}</p><p class="keyboard-hint">${this.icon("mdi:cursor-move")}${this.t("keyboard")}</p><div class="workspace-bottom"><span class="dirty-indicator" id="dirty-state"></span><div><button class="text-button" data-action="import">${this.icon("mdi:file-import-outline")}${this.t("import")}</button><button class="text-button" data-action="export" title="${this.t("exportHint")}">${this.icon("mdi:download")}${this.t("export")}</button></div></div><input id="import-file" type="file" accept=".json,application/json" hidden></section>
      <aside class="inspector" id="inspector">${this.inspectorMarkup()}</aside></div>
      <div class="sr-only" id="announcement" aria-live="polite" aria-atomic="true"></div><div id="modal-host">${this.modalMarkup()}</div>
    </main>`;
    // Seed original source strings: HTML serialization can normalize escaped
    // text, so comparing only innerHTML would still replace unchanged controls.
    for (const [selector,markup] of [["#card-selection",this.cardSelectionMarkup()],["#delivery-status",this.statusMarkup()],["#card-clipboard",this.clipboardMarkup()],["#feedback",this.feedbackMarkup()],["#modal-host",this.modalMarkup()],["#library-results",this.libraryMarkup()],["#domain",this.domainOptionsMarkup()],["#area",this.areaOptionsMarkup()],["#inspector",this.inspectorMarkup()]]) {
      const target = this.shadowRoot.querySelector(selector); if (target) this._paintedMarkup.set(target,markup);
    }
    this.paintToolbar(); this.fetchPreviewEntities();
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
  paintPreview() { const target = this.shadowRoot.querySelector("#device-preview"); if (target) target.innerHTML = this.previewMarkup(); this.fetchPreviewEntities(); }
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
  paintModalFocus() { (this._pending?.kind === "state-labels" ? this.shadowRoot.querySelector(".modal input:not([disabled])") || this.shadowRoot.querySelector(".modal button") : this._pending?.kind === "bulk-style" ? this.shadowRoot.querySelector(".modal select:not([disabled])") || this.shadowRoot.querySelector(".modal button") : this._pending?.kind === "group-paste" ? this.shadowRoot.querySelector(".modal select") || this.shadowRoot.querySelector(".modal button") : this.shadowRoot.querySelector(".modal button"))?.focus(); }
  renderModal() {
    const changed = this.paintMarkup("#modal-host",this.modalMarkup());
    if (changed && this._pending && !this.shadowRoot.querySelector("#modal-host").contains(this.shadowRoot.activeElement)) this.paintModalFocus();
  }
  paintValues() {
    this.shadowRoot.querySelectorAll('[data-action="media-stop-configure"]').forEach(button=>{
      const disabled=!this.mediaStopReady();if(button.disabled!==disabled)button.disabled=disabled;
      const card=this.cardAt(this._selectedSlot);button.setAttribute("aria-pressed",String(card?.action?.kind==="service" && card.action.service==="media_player.media_stop"));
    });
    this.shadowRoot.querySelectorAll('[data-action="media-volume-target-configure"]').forEach(button=>{button.disabled=!this.mediaVolumeTargetReady();});
    this.shadowRoot.querySelectorAll('[data-action="media-volume-configure"]').forEach(button=>{
      const disabled=!this.mediaVolumeReady(this.cardAt(this._selectedSlot),button.dataset.operation);if(button.disabled!==disabled)button.disabled=disabled;
    });
    this.shadowRoot.querySelectorAll('[data-action="media-mute-configure"]').forEach(button=>{
      const disabled=!this.mediaMuteReady();if(button.disabled!==disabled) button.disabled=disabled;
    });
    this.shadowRoot.querySelectorAll('[data-action="media-shuffle-configure"]').forEach(button=>{
      const disabled=!this.mediaShuffleReady();if(button.disabled!==disabled) button.disabled=disabled;
    });
    this.shadowRoot.querySelectorAll('[data-action="remote-configure"]').forEach(button=>{
      const disabled=!this.remotePowerReady(this.cardAt(this._selectedSlot),button.dataset.operation);
      if(button.disabled!==disabled) button.disabled=disabled;
    });
    const roomPicker=this.shadowRoot.querySelector('[data-field="vacuum-area"]');if(roomPicker) roomPicker.disabled=!this.vacuumAreas().length;
    this.shadowRoot.querySelectorAll('[data-action="vacuum-configure"]').forEach(button=>{
      const disabled=!this.vacuumOperationReady(this.cardAt(this._selectedSlot),button.dataset.operation);
      if (button.disabled!==disabled) button.disabled=disabled;
    });
    this.shadowRoot.querySelectorAll('[data-action="mower-configure"]').forEach(button=>{
      const disabled=!this.mowerOperationReady(this.cardAt(this._selectedSlot),button.dataset.operation);
      if (button.disabled!==disabled) button.disabled=disabled;
    });
    this.shadowRoot.querySelectorAll("[data-live-entity-state]").forEach(label => {
      const id = label.dataset.liveEntityState; if (!id) return;
      const value = this.libraryState(this.entityFor(id) || {entity_id:id});
      if (label.textContent !== value.state) label.textContent = value.state;
      label.classList.toggle("unavailable",!value.available);
    });
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
    const textPreview=this.shadowRoot.querySelector("[data-text-panel-preview]");
    if(textPreview)textPreview.outerHTML=this.textPanelPreviewMarkup(this.cardAt(this._selectedSlot));
    const datetimePreview=this.shadowRoot.querySelector("[data-datetime-panel-preview]");
    if(datetimePreview)datetimePreview.outerHTML=this.datetimePanelPreviewMarkup(this.cardAt(this._selectedSlot));
    const extraPreview=this.shadowRoot.querySelector("[data-extra-panel-preview]");
    if (extraPreview) extraPreview.outerHTML=this.extraPanelPreviewMarkup(this.cardAt(this._selectedSlot));
    this.shadowRoot.querySelectorAll(".preview-card[data-slot]").forEach(node => {
      const card = this.cardAt(Number(node.dataset.slot));
      if (card?.icon === "auto") {
        const icon = node.querySelector?.(".tile-icon"), name = AEH_ICONS[this.effectiveIcon(card)];
        if (icon && icon.getAttribute("icon") !== name) icon.setAttribute("icon",name);
      }
      if (card?.state_color !== true) return;
      const colors = this.paletteColors(this.effectivePalette(card));
      for (const [key,value] of [["--tile-bg",colors.background],["--tile-fg",colors.foreground]]) {
        if (node.style.getPropertyValue?.(key) !== value) node.style.setProperty(key,value);
      }
    });
  }
  paintToolbar() {
    this.paintCardSelection();
    this.shadowRoot.querySelectorAll(".modal button").forEach(button => { button.disabled = this._busy || (button.dataset.action === "modal-save" && this._conflict) || (button.dataset.action === "modal-light-control" && !this.lightControlReviewCurrent()) || (button.dataset.action === "modal-camera-preview" && (!this.cameraPreviewReviewCurrent() || !this.cameraPreviewDurationValid())) || (button.dataset.action === "modal-tile-event" && !this.tileEventReviewCurrent()) || (button.dataset.action === "modal-state-labels" && (!this.stateLabelsReviewCurrent() || this.labelsFromRows(this._pending?.rows) === null)) || (button.dataset.action === "state-label-add" && (!this.stateLabelsReviewCurrent() || this._pending.rows.length >= 8)) || (button.dataset.action === "state-label-remove" && !this.stateLabelsReviewCurrent()) || (button.dataset.action === "modal-batch-delete" && !this.selectedDeleteCurrent()) || (button.dataset.action === "modal-paste-group" && !this.groupPasteReady()) || (button.dataset.action === "modal-style-selected" && !this.selectedStyleReady()); });
    this.shadowRoot.querySelectorAll("[data-selected-style]").forEach(select => { const disabled = this._busy || !this.selectedStyleCurrent(); if (select.disabled !== disabled) select.disabled = disabled; });
    this.shadowRoot.querySelectorAll("#properties input,#properties select,#properties button,#device,[data-action=import],[data-action=export],[data-action=remove]").forEach(control => {
      control.disabled = this._busy || (control.dataset?.action === "media-volume-target-configure" && !this.mediaVolumeTargetReady()) || (control.dataset?.action === "media-stop-configure" && !this.mediaStopReady()) || (control.dataset?.action === "media-volume-configure" && !this.mediaVolumeReady(this.cardAt(this._selectedSlot),control.dataset.operation)) || (control.dataset?.action === "media-shuffle-configure" && !this.mediaShuffleReady()) || (control.dataset?.action === "media-mute-configure" && !this.mediaMuteReady()) || (control.dataset?.action === "remote-configure" && !this.remotePowerReady(this.cardAt(this._selectedSlot),control.dataset.operation)) || (control.dataset?.field==="vacuum-area" && !this.vacuumAreas().length) || (this._selectingCards && control.dataset?.action === "import") || (control.dataset?.action === "camera-preview-configure" && !this.cameraPreviewAvailability()) || (control.dataset?.field === "action-kind" && !this.sensorActionEditable(this.cardAt(this._selectedSlot))) || (control.dataset?.action === "mower-configure" && !this.mowerOperationReady(this.cardAt(this._selectedSlot),control.dataset.operation)) || (control.dataset?.action === "vacuum-configure" && !this.vacuumOperationReady(this.cardAt(this._selectedSlot),control.dataset.operation));
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
    return `.operation-options{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.operation-option{border:1px solid var(--divider-color);border-radius:18px;padding:9px 13px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit;text-align:left;cursor:pointer}.operation-option[aria-pressed="true"]{background:var(--a-tonal);color:var(--primary-text-color,#252331);border-color:var(--a-primary)}.operation-option:disabled{opacity:.45;cursor:default}
      .state-label-rows{display:grid;gap:14px;margin-top:18px}.state-label-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) 40px;gap:8px;align-items:end}.state-label-row label{display:grid;gap:6px;font-size:12px}.state-label-row input{width:100%;min-width:0;min-height:44px;padding:10px;border:1px solid var(--a-border);border-radius:12px;background:var(--a-surface);color:inherit}.state-label-row button{min-width:40px;padding:8px}
      .group-mapping{display:grid;gap:12px;max-height:min(52vh,480px);overflow:auto;margin:16px 0}.group-mapping label{display:grid;gap:6px;font-size:12px;overflow-wrap:anywhere}.group-mapping select{width:100%;min-height:44px;padding:8px;border:1px solid var(--a-border);border-radius:12px;color:inherit;background:var(--a-surface)}
      .selection-tools{display:flex;flex-direction:column;gap:10px;margin:12px 0;padding:14px;border-radius:18px;background:var(--a-tonal);font-size:12px}.selection-tools>div{display:flex;flex-wrap:wrap;gap:6px}.selection-tools p{font-size:11px;line-height:1.5;color:var(--a-muted)}.selection-tools button{font-size:11px;min-height:44px}.selection-review{max-height:240px;overflow:auto;padding-left:20px;overflow-wrap:anywhere;line-height:1.7}.preview-card[aria-disabled=true]{cursor:default}
      .status-note{flex-basis:100%;font-size:10px;line-height:1.5}.device-capabilities{margin:-8px 0 20px;border:1px solid var(--a-border);border-radius:18px;background:var(--a-surface);font-size:12px}.device-capabilities summary{padding:12px 16px;cursor:pointer;font-weight:550}.device-capabilities summary:focus-visible{outline:3px solid var(--a-primary);outline-offset:3px;border-radius:18px}.device-capabilities>div{padding:0 16px 14px}.capabilities-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px 20px;margin:0}.capabilities-grid div{min-width:0}.capabilities-grid dt{font-size:10px;color:var(--a-muted);margin-bottom:4px}.capabilities-grid dd{margin:0;overflow-wrap:anywhere;line-height:1.5}.clipboard-note{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px;margin-top:14px;border-radius:16px;background:var(--a-tonal);font-size:11px;line-height:1.5}.clipboard-note>div{flex:1;min-width:160px;overflow-wrap:anywhere}.clipboard-note p{color:var(--a-muted);font-size:10px;margin-top:4px}.clipboard-note .text-button{font-size:10px;min-height:40px}
      :host{display:block;color:var(--primary-text-color,#252331);font-family:var(--paper-font-body1_-_font-family,Roboto,system-ui,sans-serif);--a-primary:var(--primary-color,#7450c6);--a-on-primary:var(--text-primary-color,#fff);--a-bg:var(--primary-background-color,#f8f7fb);--a-surface:var(--card-background-color,#fff);--a-tonal:color-mix(in srgb,var(--a-primary) 10%,var(--a-surface));--a-border:color-mix(in srgb,var(--primary-text-color,#252331) 11%,transparent);--a-muted:var(--secondary-text-color,#6b6676);background:var(--a-bg);min-height:100vh}
      *{box-sizing:border-box}button,input,select{font:inherit}button{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:1px solid var(--a-border);border-radius:22px;min-height:44px;padding:9px 15px;color:inherit;background:var(--a-surface);cursor:pointer;transition:background .16s,box-shadow .16s,transform .16s}button:hover:not(:disabled){background:var(--a-tonal)}button:active:not(:disabled){transform:scale(.98)}button:disabled{opacity:.42;cursor:default}button:focus-visible,input:focus-visible,select:focus-visible,[role=button]:focus-visible{outline:3px solid var(--a-primary);outline-offset:4px}ha-icon{--mdc-icon-size:22px;display:inline-flex;width:var(--mdc-icon-size);height:var(--mdc-icon-size);flex:none}h1,h2,p{margin:0}h1{font-size:30px;line-height:1.15;font-weight:650;letter-spacing:-.8px}h2{font-size:18px;font-weight:600;letter-spacing:-.2px}main{max-width:1760px;margin:auto;padding:28px clamp(16px,2.2vw,40px) 36px}.app-header,.header-actions,.brand,.status-row,.section-heading,.workspace-tools,.workspace-bottom{display:flex;align-items:center}.app-header{justify-content:space-between;gap:24px;margin-bottom:20px}.brand{gap:16px}.brand-mark{width:54px;height:54px;display:grid;grid-template-columns:1fr 1fr;gap:4px;transform:rotate(-8deg);flex:none}.brand-mark i{background:var(--a-primary);border-radius:50% 50% 10px 50%}.brand-mark i:nth-child(2){opacity:.65;transform:rotate(80deg)}.brand-mark i:nth-child(3){opacity:.4;transform:rotate(185deg)}.brand-mark i:nth-child(4){opacity:.8;transform:rotate(265deg)}.eyebrow{display:block;font-size:11px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:var(--a-muted);margin-bottom:5px}.brand p{margin-top:7px;font-size:13px;color:var(--a-muted)}.header-actions{gap:12px}.device-picker{display:grid;gap:5px;font-size:11px;color:var(--a-muted);min-width:190px}.device-picker select{min-height:43px;border-radius:16px;background:var(--a-surface);padding:9px 14px}.primary{background:var(--a-primary);color:var(--a-on-primary);border-color:transparent}.primary:hover:not(:disabled){background:color-mix(in srgb,var(--a-primary) 90%,#000)}.save-button{min-height:50px;padding:12px 22px;border-radius:26px;align-self:end;font-weight:600}.status-row{gap:8px 20px;flex-wrap:wrap;font-size:11px;color:var(--a-muted);padding:12px 16px;border-radius:18px;background:var(--a-surface);margin-bottom:20px}.status-row b{font-weight:550;color:var(--primary-text-color)}.connection{display:flex;align-items:center;gap:6px}.connection i{width:7px;height:7px;border-radius:50%;background:#9c94a6}.connection.online i{background:#398064}.connection.offline i{background:#a8704b}.status-warning{color:var(--warning-color,#b26a00)}
      .editor-shell{display:grid;grid-template-columns:minmax(220px,285px) minmax(330px,1fr) minmax(245px,305px);gap:18px;align-items:start}.library,.workspace,.inspector{border:1px solid var(--a-border);border-radius:28px;background:var(--a-surface);min-width:0}.library{padding:21px 14px 16px;position:sticky;top:16px;max-height:calc(100vh - 32px);overflow:auto}.section-heading{gap:10px;padding:0 6px;margin-bottom:18px}.section-heading h2{font-size:16px}.section-symbol{display:grid;place-items:center;width:35px;height:35px;border-radius:14px;background:var(--a-tonal);color:var(--a-primary)}.search-box{display:flex;align-items:center;gap:8px;background:var(--a-bg);border:1px solid var(--a-border);border-radius:18px;padding:0 12px;min-height:46px}.search-box ha-icon{color:var(--a-muted);--mdc-icon-size:20px}.search-box input{width:100%;min-width:0;padding:12px 0;background:transparent;border:0;outline:0;color:inherit;font-size:13px}.search-box:focus-within{box-shadow:0 0 0 2px var(--a-primary)}.domain-filter{margin:10px 0 0}.domain-filter select{min-height:35px;font-size:12px;border:0;padding:6px 10px;background:transparent}.library-count{font-size:10px;color:var(--a-muted);margin:12px 7px}.entity-list{display:grid;gap:4px}.entity-row{display:flex;align-items:center;border-radius:17px;min-width:0}.entity-row:hover{background:var(--a-tonal)}.entity-main{border:0;background:none;padding:10px 3px 10px 7px;min-width:0;flex:1;justify-content:start;border-radius:17px;text-align:left;gap:9px}.entity-copy{display:flex;flex-direction:column;min-width:0;flex:1;gap:4px}.entity-copy strong{font-size:12px;font-weight:550;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity-copy small{font-size:9px;color:var(--a-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity-icon{display:grid;place-items:center;background:var(--a-bg);border-radius:12px;width:34px;height:34px;color:var(--a-primary);flex:none}.entity-icon ha-icon{--mdc-icon-size:19px}.entity-state{font-size:10px;color:var(--a-muted);max-width:50px;overflow:hidden;text-overflow:ellipsis}.entity-state.unavailable{opacity:.5}.entity-drag{width:32px;min-width:32px;min-height:44px;padding:5px;border:0;background:none;color:var(--a-muted);touch-action:none}.entity-drag ha-icon{--mdc-icon-size:18px}.empty-library{padding:20px 8px;color:var(--a-muted);font-size:13px}
      #carousel-pages{margin:8px 0 14px;color:var(--a-muted);font-size:12px}#carousel-pages summary{cursor:pointer}#carousel-pages ol{padding:0;list-style:none}#carousel-pages li{display:grid;grid-template-columns:1fr auto auto auto;gap:4px;align-items:center}#carousel-pages button{min-height:36px}
      .workspace{padding:22px;overflow:hidden;background:color-mix(in srgb,var(--a-bg) 64%,var(--a-surface))}.workspace-tools{justify-content:space-between;gap:8px}.workspace-tools h2{font-size:18px}.history-actions{display:flex;gap:3px}.icon-button{width:40px;min-height:40px;padding:8px;border:0;background:transparent;border-radius:50%}.page-tabs{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px;margin:20px 0 18px}.page-tab{font-size:11px;min-height:36px;padding:7px 12px;border:0;gap:6px;background:transparent}.page-tab ha-icon{--mdc-icon-size:16px}.page-tab.active{background:var(--a-primary);color:var(--a-on-primary)}.reserved-page{display:flex;align-items:center;gap:5px;font-size:10px;color:var(--a-muted);padding:6px;opacity:.6}.reserved-page ha-icon{--mdc-icon-size:14px}.device-stage{max-width:560px;margin:auto;padding:9px;background:#202028;border-radius:50%;box-shadow:0 20px 42px #1510221f,0 2px 8px #15102220}.screen{width:100%;aspect-ratio:1;background:#000;border-radius:50%;position:relative;container-type:inline-size;overflow:hidden;color:#fff}.screen-chrome{position:absolute;top:1.375%;left:42.375%;width:13.75%;display:flex;gap:.5cqw;align-items:center;color:#fff}.screen-chrome ha-icon{--mdc-icon-size:5.5cqw}.screen-title{position:absolute;left:27.5%;top:9.5%;width:45%;text-align:center;font-size:3cqw;line-height:1.2;color:#f5eefb}.preview-card{position:absolute;background:var(--tile-bg);color:var(--tile-fg);border:0;cursor:pointer;transition:box-shadow .16s,opacity .16s;outline:0;display:flex;justify-content:center;align-items:center}.preview-card:hover{box-shadow:inset 0 0 0 1px #ffffff70}.preview-card.selected{box-shadow:0 0 0 3px #fff,0 0 0 6px var(--a-primary)}.preview-card:focus-visible{outline:3px solid #fff;outline-offset:5px}.preview-card.drop-target{outline:5px dashed #fff;outline-offset:5px;box-shadow:0 0 0 9px var(--a-primary)}.tile-content{position:absolute;inset:0;display:flex;align-items:center;flex-direction:column;pointer-events:none;overflow:hidden;border-radius:inherit}.tile-content ha-icon.tile-icon{--mdc-icon-size:8.5cqw;position:absolute;top:21%}.tile-title,.tile-state{display:block;position:absolute;width:84%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:center;line-height:1.2}.tile-title{font-size:3cqw;bottom:23.4%}.tile-state{font-size:2cqw;bottom:11.3%;opacity:.82}.compact .tile-content .tile-icon{--mdc-icon-size:4.5cqw;top:12%}.compact .tile-title{font-size:2.5cqw;bottom:29.3%;width:88%}.compact .tile-state{font-size:2cqw;bottom:10.3%}.preview-card[data-slot="5"] .tile-content .tile-icon,.preview-card[data-slot="11"] .tile-content .tile-icon{--mdc-icon-size:5.5cqw;left:9.5%;top:29.3%}.preview-card[data-slot="5"] .tile-title,.preview-card[data-slot="11"] .tile-title{left:29.1%;top:18.1%;bottom:auto;width:60.1%;text-align:left;font-size:3cqw}.preview-card[data-slot="5"] .tile-state,.preview-card[data-slot="11"] .tile-state{left:29.1%;top:52.6%;bottom:auto;width:60.1%;text-align:left}.strip .tile-content .tile-icon{--mdc-icon-size:4.5cqw;left:9.5%;top:26.3%}.strip .tile-title{left:21.8%;top:15.8%;bottom:auto;width:66%;text-align:left;font-size:3cqw}.strip .tile-state{left:21.8%;top:56.6%;bottom:auto;width:66%;text-align:left}.data-card .tile-title{top:16%;bottom:auto;font-size:2cqw}.data-card .tile-state{top:46%;bottom:auto;font-size:4.25cqw;opacity:1}.preview-card[data-slot="13"] .tile-title{top:auto;bottom:16.1%}.preview-card[data-slot="13"] .tile-state{top:16.1%;bottom:auto}.tile-drag{position:absolute;top:5px;right:6px;z-index:1;width:32px;min-height:32px;padding:5px;border:0;background:#0002;color:inherit;opacity:0;touch-action:none;border-radius:50%}.tile-drag ha-icon{--mdc-icon-size:17px}.preview-card:hover .tile-drag,.preview-card.selected .tile-drag,.preview-card:focus-within .tile-drag{opacity:1}.hidden-card .tile-content{opacity:.3}.hidden-card{background:color-mix(in srgb,var(--tile-bg) 35%,#000);border:1px dashed #b9b2c6}.hidden-badge{position:absolute;left:50%;top:45%;transform:translate(-50%,-50%);font-size:2cqw;background:#000b;color:#fff;padding:4px 8px;border-radius:12px;pointer-events:none}.empty-card{background:#17151c;color:#aaa0b7;border:1px dashed #71677f;flex-direction:column;gap:4px}.empty-plus{font-size:6cqw;font-weight:300;line-height:1}.empty-label{font-size:2.2cqw}.screen-dots{position:absolute;bottom:7.8%;left:42%;right:42%;display:flex;gap:10%;align-items:center;justify-content:center}.screen-dots i{display:block;width:8%;aspect-ratio:1;border-radius:50%;background:#55515e}.screen-dots i.current{width:18%;aspect-ratio:2;background:#fff;border-radius:9px}.preview-caption{text-align:center;max-width:480px;margin:17px auto 0;color:var(--a-muted);font-size:11px;line-height:1.6}.keyboard-hint{display:flex;align-items:center;justify-content:center;gap:5px;color:var(--a-muted);font-size:10px;margin:10px 0 0}.keyboard-hint ha-icon{--mdc-icon-size:15px}.workspace-bottom{justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:20px;padding-top:14px;border-top:1px solid var(--a-border)}.workspace-bottom>div{display:flex;gap:2px}.text-button{border:0;background:transparent;padding:7px 9px;font-size:11px;min-height:36px;color:var(--a-primary)}.text-button ha-icon{--mdc-icon-size:17px}.dirty-indicator{font-size:10px;color:var(--a-muted)}.dirty-indicator.has-changes{color:var(--a-primary);font-weight:600}.dirty-indicator.has-changes:before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:currentColor;margin-right:6px}
      .inspector{padding:20px;position:sticky;top:16px;max-height:calc(100vh - 32px);overflow:auto}.inspector-heading{display:flex;justify-content:space-between;align-items:center;margin:-5px -7px 10px 0}.inspector h2{overflow-wrap:anywhere;margin-bottom:18px;font-size:21px;line-height:1.2}.inspector label{display:grid;gap:7px;font-size:11px;color:var(--a-muted);margin-bottom:13px}.inspector input,.inspector select{width:100%;min-width:0;min-height:43px;border:1px solid var(--a-border);border-radius:13px;padding:10px;color:var(--primary-text-color);background:var(--a-bg);font-size:12px}.inspector input[aria-invalid=true]{border-color:var(--error-color,#b3261e)}.entity-reference{font-family:ui-monospace,monospace;font-size:11px;color:var(--primary-text-color);overflow-wrap:anywhere;line-height:1.5}.property-group{border-top:1px solid var(--a-border);padding-top:17px;margin-top:6px}.property-group:first-child{padding-top:0;border:0}.property-group .text-button{margin:-7px 0 10px;padding-left:0;text-align:left;justify-content:start}.inspector .switch-row{display:flex;align-items:center;justify-content:space-between;min-height:37px;gap:12px;color:var(--primary-text-color)}.switch-row input{appearance:none;width:42px;min-height:25px;height:25px;border-radius:18px;border:0;background:#a9a1b4;position:relative;cursor:pointer;flex:none;padding:3px}.switch-row input:before{content:"";position:absolute;left:3px;top:3px;width:19px;height:19px;border-radius:50%;background:white;transition:transform .16s}.switch-row input:checked{background:var(--a-primary)}.switch-row input:checked:before{transform:translateX(17px)}.palette-swatches{display:flex;gap:7px;margin:-3px 0 14px}.palette-swatches span{width:23px;height:23px;border-radius:50%;border:1px solid var(--a-border)}.hint{font-size:10px;color:var(--a-muted);line-height:1.6;margin-bottom:13px}.inline-error,.error{color:var(--error-color,#b3261e)}.inline-error{font-size:11px;line-height:1.6}.danger{color:inherit;border-color:var(--error-color,#b3261e)}.inspector-placeholder{text-align:center;color:var(--a-muted);padding:24px 5px}.inspector-placeholder>ha-icon{--mdc-icon-size:40px;color:var(--a-primary);margin:0 auto 18px}.inspector-placeholder h2{font-size:17px;color:var(--primary-text-color);margin-bottom:9px}.inspector-placeholder p,.inspector>p{font-size:12px;line-height:1.6;margin-bottom:15px}.tonal{background:var(--a-tonal);border:0;color:var(--a-primary);font-size:12px}.feedback{font-size:12px;line-height:1.6;margin:-5px 6px 15px}.conflict{display:flex;align-items:center;gap:12px;flex-wrap:wrap;border-radius:20px;padding:13px 17px;margin-bottom:16px;background:color-mix(in srgb,var(--warning-color,#e8aa33) 13%,var(--a-surface));font-size:12px}.conflict span{flex:1}.conflict button{font-size:11px;min-height:35px}.drag-ghost{position:fixed;pointer-events:none;z-index:9999;max-width:240px;padding:13px 20px;border-radius:18px;background:var(--a-primary);color:var(--a-on-primary);font-size:13px;box-shadow:0 10px 40px #0004}
      .modal-shade{position:fixed;inset:0;z-index:10000;background:#17101f80;display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px)}.modal{max-width:470px;width:100%;padding:30px;border-radius:32px;background:var(--a-surface);box-shadow:0 24px 80px #0004;max-height:90vh;overflow:auto}.modal-symbol{width:50px;height:50px;border-radius:18px;display:grid;place-items:center;background:var(--a-tonal);color:var(--a-primary);margin-bottom:20px}.modal-symbol ha-icon{--mdc-icon-size:27px}.modal h2{font-size:25px;line-height:1.15;margin-bottom:13px}.modal>p{font-size:13px;line-height:1.65;color:var(--a-muted)}.modal-actions{display:flex;justify-content:end;gap:8px;flex-wrap:wrap;margin-top:25px}.modal-actions button{font-size:12px}.import-summary{padding:16px;margin-top:18px;background:var(--a-tonal);border-radius:18px;font-size:13px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.loading{min-height:60vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px}.loading p{max-width:500px;text-align:center;color:var(--a-muted);line-height:1.6}
      @media(hover:none){.tile-drag{opacity:.8}.entity-drag{min-width:38px;width:38px}.tile-drag{min-width:38px;min-height:38px}}@media(min-width:1500px){.workspace{padding:26px 32px}.device-stage{max-width:590px}}@media(max-width:1180px){main{padding:22px 18px}.editor-shell{grid-template-columns:minmax(205px,245px) minmax(320px,1fr)}.inspector{grid-column:1/-1;position:static;max-height:none}.inspector form{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.property-group{border-top:0;border-left:1px solid var(--a-border);padding:0 0 0 18px;margin:0}.property-group:first-child{border-left:0;padding-left:0}.property-group:last-child{grid-column:1/-1;display:flex;align-items:end;gap:20px;border-left:0;border-top:1px solid var(--a-border);padding:16px 0 0}.property-group:last-child label{min-width:230px;margin:0}.property-group:last-child .text-button{margin:0}.inspector-placeholder{padding:10px}.inspector-placeholder>ha-icon{display:none}.inspector-placeholder h2{margin:0}.header-actions{gap:8px}.device-picker{min-width:150px}}@media(max-width:760px){main{padding:18px 12px 28px}.app-header{align-items:start;flex-direction:column;gap:18px}.brand-mark{width:44px;height:44px}.brand{gap:13px}h1{font-size:27px}.header-actions{width:100%;justify-content:space-between}.device-picker{flex:1}.save-button{font-size:12px;padding:10px 17px;min-height:45px}.status-row{font-size:10px;gap:9px 14px;padding:12px;border-radius:17px}.editor-shell{display:flex;flex-direction:column;gap:14px}.workspace{order:0;width:100%;padding:17px 14px;border-radius:25px}.library{order:2;width:100%;position:static;max-height:none}.inspector{order:1;width:100%;position:static;border-radius:25px}.inspector form{display:block}.property-group,.property-group:first-child{border:0;border-top:1px solid var(--a-border);padding:17px 0 0;margin-top:8px}.property-group:first-child{border-top:0;padding-top:0}.property-group:last-child{display:block}.property-group:last-child label{min-width:0;margin-bottom:16px}.entity-list{max-height:320px;overflow:auto}.entity-copy strong{font-size:13px}.entity-copy small{font-size:10px}.page-tabs{gap:3px;margin-top:15px}.page-tab{font-size:10px;padding:7px 10px}.reserved-page{font-size:9px;padding:5px 2px}.reserved-page ha-icon{display:none}.workspace-tools h2{font-size:16px}.workspace-bottom{margin-top:16px;gap:8px}.workspace-bottom>div{margin-left:auto}.text-button{font-size:10px}.device-stage{padding:7px;max-width:510px}.modal{padding:24px;border-radius:27px}.modal h2{font-size:23px}.modal-actions{gap:6px}.modal-actions button{font-size:11px;padding:9px 12px}.preview-caption{font-size:10px}.keyboard-hint{font-size:9px}}
      @media(prefers-reduced-motion:reduce){*,*:before{transition:none!important;scroll-behavior:auto!important}}
    `;
  }
}
if (!customElements.get("atmosfera-tile-editor")) customElements.define("atmosfera-tile-editor",AtmosferaTileEditor);
