# Unknown PIgame

## *Description
Single Player, Platformer Permadeath, Random upgrades, Speedrun   
### *Controls
** W D**: *Movement*
**Spacebar**: *Jump*
**C**: *Pause game*
### *Progression
- Your goal is to beat your time during each run, to earn more point while running from a monster that tries to kill you
- The point are used to buy increased chances of a specific trait
- The only win condition is to go below a certain time
## *Feature
**Collision detection:** Check when/if the character hit a hurt box or a collision.

**Time tracking tracking:**  Keeps a running total of the player's time.

**Point system** Calculate how many coins per seconds shaved off best run to buy % increasers, creating a fun gameplay loop that gets harder the better you are

**Random upgrades** At the start of the levels there is a random chance to ga get an upgrade, the chance to get certain upgrades can be increased.
>The powerup are Speed, Jumb, Half of the time, and Extra Life
## *Installation / How to Run
Follow these  instructions to get the game running:
1. Clone this repository on git hub and extract the files
2. Install Python
3. Open **Windows PowerShell**
4. Navigate to folder using *cd* "change directory" and ls to navigate files
5. Start the game by running: **py. Pi-game**
## *Team Members and Roles
**Muhammed**: Level designer/ Programmer -
> Creates levels in Physical form and help with programing assets]

**George**:  Artist/ Programmer -
>Draws the Characters, Background and other assets and helps with coding

1.	We fixed the background completely with a scrolling factor that allows the character to move across multiple backgrounds. Also, we made a randomizer for the parkour platforms to form, which helps with the repetition problem. We made a store / ending screen for the death of the character, which also is going to contain the powerups and description. We have started to implement the code for the power ups as well, which are a speed boost, jump boost, extra life and half-time for the counter. Lastly, we also made a monster that chases the character until the end of the run, which acts as the enemy / villain, that makes you lose as soon as he catches up to you. 

2.	Creating a start screen, such as the one in geometry dash, where you can choose when to start the game and continue/restart when you choose to. We want to create this change to help the game run smoothly and look even better.


Finals:
1. The game includes player movement, jumping, scrolling backgrounds, platform collisions, floor collisions, monster following the player, powerups, and a death screen. The player moves throuhg a side-scorlling game while running away from the monster that follows you across the map. Platforms are randomly generated, and powerups can increase your speed, boos your jumps, add extra lives to your run, and reduce the timers speed so you can get a faster time. The game currently has all of these systems working properly.
2. Some bugs include collision issues where the player can get stuck or bug around platforms. The monster is very simple and can be bugged due to the speed power up because it moves as fast as the player but not the background which bugs the whole game. If I had more time, I would improve the collision system, add better enemy designs, and debug the game with the monster, I would also add more levels and overall polish the game up more. 
