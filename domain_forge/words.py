"""Compact word lists for split detection and generic-name penalties.

Not a dictionary of the language. Just enough English to tell 'northstar'
from 'xqztpv' and to punish names nobody would put on a business card.
"""

from __future__ import annotations

STOPWORDS = frozenset(
    """
    a an the and or but if of to for in on at by with from as is was are were
    be been being this that these those it its you your we our they them my
    """.split()
)

# Imageable stems. A name that contains one of these can be pictured.
# Used by the love scorer, not the generator.
IMAGE = frozenset(
    """
    dawn nova lumen seed root vera prism prime origin light first aurora
    aether star sun moon fire water earth sky sea wind rose hawk wolf
    oak pine river stone glass gold iron silver snow rain dusk ember
    spark flame dawnlight
    """.split()
)

# Ultra-generic SLDs. People do not fall in love with these; they forget them.
GENERIC = frozenset(
    """
    app apps web net netted site sites online digital data cloud host hosts
    mail email shop store blog news game play meta open free best top my the
    get try use go tech ai io hq lab labs info biz xyz corp inc llc company
    official website portal world global smart super ultra mega proto demo
    test staging prod dev server api platform system software service
    services solution solutions group holdings international
    """.split()
)

# Short, real words used to detect concatenations (north+star, open+road).
WORDS = frozenset(
    """
    ace act age aid air all alpha amber ant apex arc arch ark art ash atlas
    atom aura axis bay beam bear beat bell berry bird bit black bloom blue
    bolt bond bone book boom boot born bow box brand brave brick bright
    brook brush bud bulb bulk bull burn byte cabin cake calm camp cane cap
    car card care cart cast cat cave cedar cell chain chalk charm chase
    chat chip city clam clap clay clear cliff clone cloud clover club coal
    coast cob code coil coin cold colt comb come cone cook cool cop copper
    coral core cork corn cost couch cove crab craft crag crane crash crate
    crew crop crow crowd crown cry cube cup curb cure curl curve cut daisy
    dale dart dash data dawn day deck deep deer delta dew dial dice dock
    doe dog doll dome door dot dove down dragon draw drift drop drum dry
    duck dune dusk dust eagle ear earth east echo edge eel egg elm ember
    end engine era eve even ever eye face fact fade fair fall fan far farm
    fast fate fawn fear feather fern field fig film fin find fire firm fish
    fist flag flame flare flash flat flax fleet flesh flint flock flood
    floor flow flower fly foam fog foil fold folk font food fool foot ford
    forest fork form fort fox frame frost fruit fuel full fur fuse gain
    gale game gap gate gear gem giant gift gill glad glass gleam glen glow
    glue goal goat gold golf good goose gore grain grand grape graph grass
    grave gray green grid grim grin grip grit grove grow guild gulf gum gun
    gust gym hail hair hale half hall halo hand harbor hard hare hart hat
    hatch haunt have hawk hay head heal heap hear heart heat heaven hedge
    heel helm help hen herb herd here hero heron hide high hill hinge hint
    hip hive hold hole holly home honey hook hop hope horn horse host hot
    hour house howl hub hue hug hull hum hunt hut ice icon idea idle inch
    ink inn iris iron island ivory ivy jack jade jam jar jaw jay jet jewel
    join joke jolt jot joy judge juice jump june jungle jury just keel keep
    kelp key kick kid kiln kilt kin kind king kit kite kiwi knife knight
    knot lace lack lake lamb lamp land lane lap lark laser last latch late
    laugh law lawn lead leaf leap learn leather leave ledge left leg lemon
    lens leopard let letter level lever lid life lift light lily limb lime
    line link lion lip list live load loaf loan local lock lodge log logo
    lone long look loop lord lose loss lot loud love low luck lump lunar
    lunch lung lure lye lynx lyre mail main major make maple marble march
    mark marsh mask mass mast match mate math maze meal mean meat medal
    media melt memo mend mesh metal meter micro mid milk mill mind mine
    mint mirror mist mite mix mock mode mold mole monk month moon moose
    more moss moth motion motor mount mouse mouth move mow mud mule muse
    mush music musk mute myth nail name navy near neck need neon nest net
    new next nice night nine node noon north nose note nova now number oak
    oar oasis oat ocean odd ode oil old olive omega open orange orbit ore
    organ otter ounce oven over owl ox oxide oyster pace pack pad page
    pail pain paint pair pale palm pan pane paper park part pass past path
    paw peak pear pearl peat peck peel pen pencil pepper perch pet phase
    phone photo piano pick pie piece pig pike pile pill pine pink pint pipe
    pit pitch pixel place plan plane plant plate play plot plow plug plum
    plus pod poem poet point poke pole pond pony pool pop porch port post
    pot potato pound pour powder power praise press prey price pride prime
    print prize probe proof proud puff pull pulse pump punch pupil puppy
    pure push quail quark quartz queen query quest queue quick quiet quilt
    quiz race rack radar radio raft rag rail rain raise rake ram ramp ranch
    range rank rapid rare rasp rat rate raven raw ray razor reach read
    ready real red reed reef reel rest rib rice rich ride ridge rifle right
    rim ring riot rip rise river road roar roast rob rock rod roll roof
    room root rope rose rot rough round route row royal rub ruby rug ruin
    rule rum run rune rush rust rye sack saddle safe sage sail saint sake
    salad sale salt same sand sap satin sauce save saw scale scan scar
    scare scarf scene scent school scoop scope score scout scrap screen
    screw sea seal seam search season seat seed seek seem self sell send
    sense set seven shade shadow shaft shake shale shall shame shape share
    shark sharp shawl she shear shed sheep sheet shelf shell shift shine
    ship shirt shock shoe shoot shop shore short shot shoulder shout show
    shred shrimp shrine shrub shrug side sieve sight sign silk silo silver
    simple sin sine sing sink sip sir sit six size skate ski skill skin
    skip skull sky slab slack slag slain slam slang slap slash slate slave
    sled sleep sleet sleeve slice slick slide slim slime sling slip slit
    slope sloth slow slug smash smell smile smith smoke snack snail snake
    snap snare snarl sneak snow snug soak soap soar sock soda sofa soft
    soil solar sole solid solo solve some son song soon soot sore sort
    soul sound soup sour south sow space spade span spark sparrow spawn
    speak spear spec speed spell spend spice spider spike spill spin spine
    spirit spit splash split spoil spoke sponge spoon sport spot spray
    spread spring sprout spur square squash squid stack staff stag stage
    stain stair stake stale stalk stall stamp stand star starch stare
    start stash state station stay steak steal steam steel steep steer
    stem step stern stick stiff still sting stir stitch stock stone stool
    stop store stork storm story stout stove straw stray stream street
    stress stretch stride strike string strip stripe strive stroke strong
    strut stub stuck study stuff stump stun style such sugar suit sulk sum
    sun super surf surge swan swap swarm sway swear sweat sweep sweet
    swell swift swim swing swirl switch sword sworn syrup table tack tail
    take tale talk tall tame tan tank tap tape tar task taste tea team
    tear tech tell ten tend tent term test text than thank that thaw the
    then theory there these they thick thief thigh thin thing think third
    this thorn those thread three throat throw thumb thunder tick tide
    tidy tie tiger tight tile till time tin tip tire title toad toast toe
    toil token told toll tomato ton tone tongue tool tooth top torch torn
    toss total touch tough tour tow towel tower town toy trace track trade
    trail train trait tramp trap trash travel tray tread treasure tree
    trek trial tribe trick trim trip troop trout truck true trumpet trunk
    trust truth try tub tube tuck tug tuna tune tunnel turf turn turtle
    tusk tutor tweet twelve twenty twin twist type ugly uncle under union
    unit unity until upon upper urge us use used user valley value van
    vapor vase vast vault veal vein velvet vendor venom vent verb verse
    very vessel vest veto vice video view village vine violet violin
    virus visa vise visit visor voice void volt volume vote vow vowel
    voyage wad wage wagon waist wait wake walk wall walnut walrus wand
    want war ward warm warn warp warrior was wash wasp waste watch water
    wave wax way weak wealth weapon wear weasel weather web wedding wedge
    week weep weigh weird welcome well west wet whale wharf what wheat
    wheel when where which while whip whirl white who whole why wick wide
    widow width wife wild will willow win wind window wine wing wink
    winter wipe wire wise wish wit witch with wolf woman wonder wood wool
    word work world worm worry worse worth would wound woven wrap wreath
    wreck wren wrench wrestle wring wrist write wrong yard yarn yawn year
    yeast yellow yes yet yield yolk you young youth zeal zebra zero zest
    zinc zip zone zoo
    """.split()
)


def is_stopword(sld: str) -> bool:
    return sld in STOPWORDS


def is_generic(sld: str) -> bool:
    return sld in GENERIC
