
import Classes.player as player
import Classes.village as village
import random

class base_controller(player.Player):

		def __init__(self, name, quadrant, race, ai_controller,
				 population=0, attack_points=0, defence_points=0, raid_points=0, culture_points=0,
				 villages=[], AI_type = 'generic'):
			super().__init__(name, quadrant, race, ai_controller,
					population=0, attack_points=0, defence_points=0, raid_points=0, culture_points=0, villages=[])

		def reset_next_action(self, upgrade_time):
			  
			if upgrade_time != []:
				 self.next_action = upgrade_time
			else:
				 #issue - this is hardcoded into the AI as a "wait 20k seconds" element - should be dynamic and
				 #controlled at a high level
				 self.next_action = 20000
			#issue - this function doesn't return anything, but it should absolutely log stuff

		def will_i_act(self, current_time, global_last_active):
			 
			#variable used to determine if the player is taking an action
			player_acting = False

			#removed old legacy if sleep == False check
			duration_slept = current_time - global_last_active
			local_duration_slept = current_time - self.Last_Active

			if duration_slept == self.next_action:
				 #issue - at this point there should be some logging to reflect actions taken

				#if we're taking an action, update the last active flag to reflect doing something
				self.Last_Active = current_time

				#if multiple villages exist, we may need multiple wait times, therefore building it in now
				#issue - this actually wakes up all villages for a player every time one of them needs to be
				#thats suboptimal behaviour - low priority, but still an issue
				wait_time_list = []
				for curr_village in self.villages:
					#this used to use map data to find the village, it should now find it within the players
					resources_gained = curr_village.yield_calc()
					for i in range(len(resources_gained)):
						resources_gained[i] *= local_duration_slept
					current_stockpile = self.stored
					current_max = curr_village.storage_cap
					for i in range(len(resources_gained)):
						if(resources_gained)[i] + current_stockpile[i] > current_max[i]:
							current_stockpile[i] = current_max[i]
						else:
							current_stockpile[i] = current_stockpile[i] + resources_gained[i]
					curr_village.stored = current_stockpile

					#check to see if there was a village that was currently upgrading
					#issue - this currently just assumes that if you've woken up, then you've finished
					#this is obviously not true, and we need to change this. Left as is for now
					#issue - this is incredibly messy as a result of needing to handle both villages and fields
					#i hate it and it needs to change to be better, also for romans.
					if len(curr_village.currently_upgrading) > 0:
						if len(curr_village.currently_upgrading) == 2:
							upgraded_building = curr_village.currently_upgrading
							curr_village.building_upgraded(upgraded_building)
						else:
							upgraded_field = curr_village.currently_upgrading
							curr_village.field_upgraded(upgraded_field)

					#now we get possible buildings
					possible_actions = curr_village.possible_buildings()


					##now we need to get the actual action, but at present, this is not possible.
					#if ai_controller = none, it will use full randomness
					#issue - we need a full random AI, which will utilise the below logic, and then plug in via derive next action
					if self.ai_controller == None:
						merged_list = []
						origin_list = []
						for key in possible_actions:
							hold_list = possible_actions[key]
							for item in hold_list:
								merged_list.append(item)
								origin_list.append(key)
						
						if len(merged_list) == 0:
							chosen_item = None
							chosen_origin = None
						else:
							index = random.randint(0, len(merged_list) - 1)
							chosen_item = merged_list[index]
							chosen_origin = origin_list[index]
					else:
						#all ai controllers will use a function called "derive next action, called here"
						self.ai_controller.derive_next_action()
					


					#initiate the chosen upgrade
					#but we have a check to make sure we're not currently upgrading something
					if len(curr_village.currently_upgrading) != 0:
						raise ValueError("I have tried to initiate an upgrade, but I'm already upgrading something - why?")
					else:
						#if I have no valid upgrade options, pass, and the above logic sets that to the 20k
						if chosen_item == None:
							pass
						else:
							reset_time = True
							#dual options to account for the dual structure
							#issue - this is a huge headache and will only get worse, i really need to resolve this
							if chosen_origin == 'buildings':
								wait_time = curr_village.upgrade_building(chosen_item)
							if chosen_origin == 'fields':
								wait_time = curr_village.upgrade_field(chosen_item)
							wait_time_list.append(wait_time)

					if reset_time == True:
						true_wait_time = min(wait_time_list)
						self.reset_next_action(true_wait_time)
					else:
						#issue - i'm passing an empty list here. This is unneeded, as its already done above
						#but its actually cleaner logic to have it live here, as the building may not be upgraded
						self.reset_next_action([])
						true_wait_time = self.next_action

			else:
				#helps the ticker advance.
				#issue - i still don't think i follow precisely how this works. don't raise as issue, but ammend comment with explanation
				self.next_action -= local_duration_slept
				true_wait_time = self.next_action
			
			return true_wait_time

			


							



					

												 
					
					




			 
			
		
				
			
