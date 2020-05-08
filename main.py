import numpy as np
from tkinter import *
import thinkdsp
import sounddevice as sd


root = Tk()
root.title("Synthesiser")

samplingFreq = 44100  # Hz


def clickBtn(note):
    volume = 0.1  # range [0.0, 1.0]
    duration = 1.0  # in seconds, may be float

    original_samples = (np.sin(2 * np.pi * np.arange(samplingFreq * duration) * note / samplingFreq)).astype(np.float32)

    wave = waveform(note, n.get())

    spectrum = wave.make_spectrum()
    spectrum.low_pass(slider2.get())
    spectrum.high_pass(slider3.get())
    filtered = spectrum.make_wave()

    new = resonance(filtered.ys, samplingFreq, slider1.get(), slider4.get())

    sd.play(new.real, samplingFreq)
    sd.wait()


def waveform(freq, btn_input):
    if btn_input == 1:
        signal = thinkdsp.SinSignal(freq)
    if btn_input == 2:
        signal = thinkdsp.SquareSignal(freq)
    if btn_input == 3:
        signal = thinkdsp.TriangleSignal(freq)

    wave = signal.make_wave(framerate=samplingFreq)
    return wave


def resonance(inputsignal, sampleFreq, a, b):
    # centerFrequency = 2*np.pi*((sampleFreq/100)*a)/sampleFreq  # make the centerFreq scalable by 0-100% of the samplingFreq
    # bandwidth = 2*np.pi*((sampleFreq/100)*b)/sampleFreq  # make the bandwidth scalable by 0-100% of the samplingFreq

    centerFrequency = 2 * np.pi * a / sampleFreq
    bandwidth = 2 * np.pi * b / sampleFreq

    poleRadius = (2 - bandwidth) / 2
    poleAngle = np.arccos(2 * poleRadius * np.cos(centerFrequency) / (1 + poleRadius**2))
    gain = (1 - poleRadius**2) * np.sin(poleAngle)

    length = np.size(inputsignal)
    output = np.zeros(length)
    iirCoefficients = np.array([2*poleRadius*np.cos(poleAngle), -poleRadius**2])
    print(iirCoefficients[0])
    print(iirCoefficients[1])

    for n in np.arange(length):
        if n < 2:
            output[n] = inputsignal[n]
        else:
            output[n] = gain * inputsignal[n] + 2 * poleRadius * np.cos(poleAngle) * output[n - 1] - poleRadius**2 * output[n - 2]
            # output[n] = inputsignal[n] + iirCoefficients[0] * output[n - 1] - iirCoefficients[1] * output[n - 2]
    return output / max(output)


############################ GUI ####################################

radFrame = LabelFrame(root, text="Waveforms", padx=5, pady=5)
radFrame.pack(fill=X)

sliderFrame = LabelFrame(root, text="Filters", padx=5, pady=5)
sliderFrame.pack(fill=X)

btnFrame = LabelFrame(root, text="Notes", padx=5, pady=5)
btnFrame.pack(fill=X)

n = IntVar()  # only one variable to be used by multiple radiobuttons so only one of them can be active
n.set("1")

Radiobutton(radFrame, text="Normal waveform", variable=n, value=1).pack(anchor="w")  # grid(row=0, column=0)
Radiobutton(radFrame, text="Square waveform", variable=n, value=2).pack(anchor="w")  # grid(row=1, column=0)
Radiobutton(radFrame, text="Triangular waveform", variable=n, value=3).pack(anchor="w")  # grid(row=2, column=0)


btn1 = Button(btnFrame, text="A3", padx=20, pady=30, command=lambda:clickBtn(220))  # fg="white", bg="black",
btn1.pack(side=LEFT)

btn2 = Button(btnFrame, text="B3", padx=20, pady=30, command=lambda:clickBtn(246))
btn2.pack(side=LEFT)

btn3 = Button(btnFrame, text="C4", padx=20, pady=30, command=lambda:clickBtn(261))
btn3.pack(side=LEFT)

btn4 = Button(btnFrame, text="D4", padx=20, pady=30, command=lambda:clickBtn(293))
btn4.pack(side=LEFT)

btn5 = Button(btnFrame, text="E4", padx=20, pady=30, command=lambda:clickBtn(329))
btn5.pack(side=LEFT)

s1Label = Label(sliderFrame, text="Resonator").grid(row=0, column=1)
s2Label = Label(sliderFrame, text="Equalizer").grid(row=0, column=5)

placeholder = Label(sliderFrame, text="                           ").grid(row=0, column=3)

slider1 = Scale(sliderFrame, from_=1, to=1000, orient=HORIZONTAL, label="Center Freq")
slider1.set(500)
slider1.grid(row=1, column=1)

slider2 = Scale(sliderFrame, from_=1, to=1000, orient=HORIZONTAL, label="Low")
slider2.set(1000)
slider2.grid(row=2, column=5)

slider3 = Scale(sliderFrame, from_=1, to=1000, orient=HORIZONTAL, label="High")
slider3.grid(row=1, column=5)

slider4 = Scale(sliderFrame, from_=0, to=500, orient=HORIZONTAL, label="Bandwidth")
slider4.grid(row=2, column=1)

root.mainloop()



