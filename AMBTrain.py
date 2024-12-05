import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer

train_texts = [
    # Ambiguous instructions (label 0)
    "Adjust the settings as necessary.",
    "Check all connections thoroughly.",
    "Ensure the device is properly configured.",
    "Install the module carefully.",
    "Prepare the equipment for operation.",
    "Secure all fittings appropriately.",
    "Inspect the unit for abnormalities.",
    "Maintain optimal operating conditions.",
    "Set up the system according to guidelines.",
    "Apply power and observe the results.",
    "Consult the manual for further instructions.",
    "Adjust parameters to improve efficiency.",
    "Ensure compliance with standards.",
    "Observe all warning signs",
    "GATHER ALL NECESSARY ITEMS, INCLUDING PARTS, TOOLS, MATERIAL, ETC., BEFORE BEGINNING PM.",
    "Make sure to use the correct PPE when cleaning the tools",
    "WHEN THE FURNACE IS AVAILABLE FOR PM, CHANGE THE MACHINE STATE TO REFLECT THE PM AND SIGN-ON.",
    "GET A CLEAN SIC BOAT/PEDESTAL FROM THE STORAGE OVENS AND UPDATE THE SERIAL NUMBERS OF THE QUARTZWARE ON THE WEB BASED QUARTZWARE MANAGE SYSTEM.",
    "REMOVE THE GAS FLEX LINES",
    "INSTALL THE O-RING AND TEFLON GUIDE TO THE MANIFOLD.",
    "Verify no wafers or cassettes are loaded onto the tool.",
    "Spin down the Turbos.",
    "Turn off power to compressor with the breaker",
    "Install the new socket",
    "Install clean/new Flange",
    "Shutdown Terminal Roughing Pump",
    "Install bottom flange on Exhaust tube to Silencer/Muffler",
    "Remove and clean elevator isolation valves.",
    "Complete Centerline setup for the traveling faraday",
    "Use NSK#2",
    # Specific instructions (label 1)
    "Set the power supply to 12V DC output.",
    "Connect the negative lead to ground terminal GND1.",
    "Solder resistor R15 (10kΩ) to position R15 on the PCB.",
    "Apply 2.5 Nm torque to screw S3 using a calibrated torque screwdriver.",
    "Update the software to version 5.4.2 using the update utility.",
    "Configure the device IP address to 192.168.0.10 with a subnet mask of 255.255.255.0.",
    "Mount the heatsink onto the processor using thermal paste TP-100.",
    "Set jumper JP2 to position 'B' for normal operation mode.",
    "Measure the resistance between points TP5 and TP6; it should be 50Ω ±5%.",
    "Replace capacitor C7 with a 220μF, 16V electrolytic capacitor.",
    "Install firmware using the 'flash_firmware.sh' script via the command line.",
    "Enter the BIOS setup by pressing F2 during startup and enable virtualization.",
    "Attach the ribbon cable to connector J12 with the red stripe aligned to pin 1.",
    "Set potentiometer RV1 to 2.5kΩ using a multimeter.",
    "Program the FPGA with the 'config.bit' file using the JTAG interface.",
    "Insert the SD card into slot SD1 and format it to FAT32 filesystem.",
    "Activate relay K1 by sending a high signal to GPIO pin 17.",
    "Set the clock frequency to 16 MHz via the system configuration tool.",
    "All scheduled maintenance is to be performed by CMP/IMP equipment engineering or trained personnel.",
    "BEFORE PM PROCEDURE FOR THE FURNACE, MAKE SURE TO REVIEW AND FOLLOW THE PROCEDURES IN THE TEL FURNACE LOTO PROCEDURE SPEC AT http://dles285com/d222doc/VFT/active/VFT.doc",
    "CONTACT THE EE TOOL OWNER TO VERIFY THAT THE PM CAN BE PEFORMED AND THAT THER ARE NO SPECIAL INSTRUCTIONS OR REQUIREMENTS (I.E. TOOL/SOFTWARE UPGRADES,ETC.)",
    "CONTACT RESPONSIBLE MANUFACTURING SUPERVISOR AND PE FOR THE FURNACE THAT WILL BE UNDERGOING THE MAINTENANCE WORK TO ENSURE NO TIME SENSITIVE MATERIAL WILL MISS TIME WINDOW DUE TO THE PM.",
    "HANDLE NEW/CLEAN QUARTZWARE WITH ACID GLOVES AND NEW/CLEAN SIC QUARTZWARE WITH ACID GLOVES AND CLEAN ROOM WIPES AS A BARRIER BETWEEN THE ACID GLOVES AND SIC QUARTZWARE.",
    "DO NOT ALLOW IPA TO TOUCH THE BOAT ROTATION SEAL SHAFT. IPA CAN SEEP INTO THE ROTATION SEAL DAMAGING THE FERROFLUIDIC SEAL",
    "LOG ONTO FURNACE IN SMS AND PLACE FURNACE MISTI ID INTO SMR STATE",
    "DISCHARGE ALL DUMMY WAFERS. (SIDE AND EXTRA DUMMIES)",
    "REMOVE AUTOSHUTTER QUARTZ AND O-RING AND CLEAN AUTOSHUTTER WITH DI WATER. REPLACE AUTOSHUTTER O-RING AND QUARTZ.",
    "Select range for past the 90 mark and press the bin next to the Archive logs button to delete.",
    "Look for fraying or broken connections.",
    "Ohm from tip of grounding rod to ground and ensure it is less than 0.1 Ω. If greater than that fix the connection or replace grounding rod.",
    "Check Helium pressure on compressors. Add Helium if below 240 psig. Remove Helium if above 250 psig",
    "Verify that all process debris is wiped out, and there is no trace of broken wafer or other silicon debris in the chamber. If any bubbling or flaking is present on the walls, use Scotchbrite, IPA and DI water to remove.",
    "If the diff seals gauge is over 2 Torr, close all the valves in the tree except the inlet. If the gauge doesn’t drop below 1 Torr then leak check the pumping line and 7.32. repair. If no leaks are found ensure the pump/booster is running and submit a pump work order as needed to achieve 1 Torr or lower.",
    "If tool is IM108 or IM107 check remote light towers next to IM101. Replace bulbs (4094545-001) if necessary.",
    "Using a meter check from pin to tool ground. Continuity must be < 0.5 Ω.",
]

train_labels = [
    0,  # Ambiguous
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,  # Specific
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
]

val_texts = [
    # Ambiguous instructions (label 0)
    "Adjust as needed for optimal performance.",
    "Verify that everything is functioning correctly.",
    "Run 13 on left side",
    "Shut down the beam.",
    "If red light remains on then Ref to Varian PSB 2616B. Contact tool owner.",
    "Replace the D2 suppression lens.",
    "Connect leak checker to bearing outer seal rough line via leak check port.",
    "Mark empty cylinders as empty (MT), place in the dumbwaiter and notify the Chemical Dock.",
    "Turn off the source gas, arc and Filament.",
    "Ensure the high voltage interlock is enabled or that the source cabinet is in bypass mode",
    "Clean around the tool and in the ES area.",
    "Tune up E-ALIGNMENT-G.",
    # Specific instructions (label 1)
    "Set the temperature controller to 75°C with a tolerance of ±1°C.",
    "Connect sensor S1 to analog input AI3 on the control module.",
    "Using dummy wafer cross slot a wafer to sit in position 12 and 13 of the cassette.",
    "If tool does not detect the cross slotted wafer perform the wafer mapping sensor setup Reference 6.4.5 VMM on the faulty Endstation.",
    "Ensure beams are stable and at least 10% away from alarm limits.",
    "Ensure the high voltage interlock is enabled or that the source cabinet is in bypass mode. The red lamp on right side of the enclosure will be flashing when the high voltage interlock is made.",
    "MISTI comments after bottle changes must include the names of people who worked on the bottle change procedure. Comments should also indicate if the respirator was inspected prior to use and disinfected after use.",
    "Open the regulator valve fully when prompted",
    "The signal is clean and free of noise (no arcing)",
    "Both Red and Green indicator light should be lit.",
    "Slide the D2 lens sub-assembly out of the housing.",
    "Touch the yes button when prompted to signal the completion of the gas change procedure."

]

val_labels = [
    0,  # Ambiguous
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,  # Specific
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
]

class TextClassificationDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=max_length)
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)

device = torch.device('cpu')
if torch.cuda.is_available():
    device = torch.device('cuda')

tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
model = AutoModelForSequenceClassification.from_pretrained('allenai/scibert_scivocab_uncased', num_labels=2)
model.to(device)

train_dataset = TextClassificationDataset(train_texts, train_labels, tokenizer)
val_dataset = TextClassificationDataset(val_texts, val_labels, tokenizer)

training_args = TrainingArguments(
    report_to=None,
    output_dir='./results',
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    eval_strategy='epoch',
    save_strategy='epoch',
    logging_dir='./logs',
    logging_steps=10,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()

model_path = 'scibert_scivocab_AMB_uncased'
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)