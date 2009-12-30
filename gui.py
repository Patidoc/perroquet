# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Frédéric Bertolus.
#
# This file is part of Perroquet.
#
# Perroquet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Perroquet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.


import gtk, time, urllib, re

class Gui:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("gui.xml")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("MainWindow")
        self.typeLabel = self.builder.get_object("typeView")

        self.initTypeLabel()

        filefilterSave =self.builder.get_object("filefilterSave")
        filefilterSave.add_pattern("*.perroquet")

    def on_MainWindow_delete_event(self,widget,data=None):
        if self.core.IsAllowQuit():
            gtk.main_quit()
            return False

        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                                   "Do you really quit without save ?")
        dialog.set_title("Confirm quit")

        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_YES:
            gtk.main_quit()
            return False # returning False makes "destroy-event" be signalled
                         # for the window.
        else:
            return True # returning True avoids it to signal "destroy-event"





    def on_newExerciceButton_clicked(self,widget,data=None):
        self.newExerciceDialog = self.builder.get_object("newExerciceDialog")

        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        exerciceChooser = self.builder.get_object("filechooserbuttonExercice")
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")
        videoChooser.set_filename("None")
        exerciceChooser.set_filename("None")
        translationChooser.set_filename("None")
        self.newExerciceDialog.show()



    def on_buttonNewExerciceOk_clicked(self,widget,data=None):
        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        videoPath = videoChooser.get_filename()
        exerciceChooser = self.builder.get_object("filechooserbuttonExercice")
        exercicePath = exerciceChooser.get_filename()
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")
        translationPath = translationChooser.get_filename()
        if videoPath == "None" or videoPath == None:
            videoPath = ""
        if exercicePath == "None" or exercicePath == None:
            exercicePath = ""
        if translationPath == "None" or translationPath == None:
            translationPath = ""

        print translationPath

        self.core.SetPaths(videoPath,exercicePath, translationPath)
        self.newExerciceDialog.hide()

    def on_buttonNewExerciceCancel_clicked(self,widget,data=None):
        self.newExerciceDialog.hide()

    def monclic(self, source=None, event=None):
        self.widgets.get_widget('label1').set_text('Vous avez cliqué !')

        return True

    def SetCore(self, core):
        self.core = core

    def GetVideoWindowId(self):
        return self.builder.get_object("videoArea").window.xid

    def SetSequenceNumber(self, sequenceNumber, sequenceCount):
        ajustement = self.builder.get_object("adjustmentSequenceNum")
        sequenceNumber = sequenceNumber + 1
        self.settedSeq = sequenceNumber
        ajustement.configure (sequenceNumber, 1, sequenceCount, 1, 10, 0)
        self.builder.get_object("labelSequenceNumber").set_text(str(sequenceNumber) + "/" + str(sequenceCount))

    def SetSequenceTime(self, sequencePos, sequenceTime):
        if sequencePos > sequenceTime:
            sequencePos = sequenceTime
        if sequencePos < 0:
            sequencePos = 0
        self.settedPos = sequencePos /100
        ajustement = self.builder.get_object("adjustmentSequenceTime")
        ajustement.configure (self.settedPos, 0, sequenceTime/100, 1, 10, 0)
        textTime = round(float(sequencePos)/1000,1)
        textDuration = round(float(sequenceTime)/1000,1)
        self.builder.get_object("labelSequenceTime").set_text(str(textTime) + "/" + str(textDuration) + " s")

    def SetPlaying(self, state):
        self.builder.get_object("toolbuttonPlay").set_sensitive(state)
        self.builder.get_object("toolbuttonPause").set_sensitive(not state)

    def SetCanSave(self, state):
        self.builder.get_object("saveButton").set_sensitive(state)

    def SetWordList(self, wordList):
        self.wordList = wordList
        self.UpdateWordList()


    def UpdateWordList(self):
        buffer = self.builder.get_object("textviewWordList").get_buffer()
        entry = self.builder.get_object("entryFilter")

        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)


        formattedWordList = ""

        regexp = entry.get_text()

        try:
            re.search(regexp,"")
        except re.error:
            regexp = ""
            pass

        for word in self.wordList:
            if re.search(regexp,word):
                formattedWordList = formattedWordList + word + "\n"

        iter = buffer.get_end_iter()
        buffer.insert(iter,formattedWordList)

    def SetTranslation(self, translation):
        textviewTranslation = self.builder.get_object("textviewTranslation").get_buffer()
        textviewTranslation.set_text(translation)

    def SetStats(self, sequenceCount,sequenceFound, wordCount, wordFound, repeatRate):
        labelProgress = self.builder.get_object("labelProgress")
        text = ""
        text = text + "- Sequences: "+str(sequenceFound)+"/"+str(sequenceCount)+" ("+str(round(100*sequenceFound/sequenceCount,1))+" %)\n"
        text = text + "- Words: "+str(wordFound)+"/"+str(wordCount)+" ("+str(round(100*wordFound/wordCount,1))+" %)\n"
        text = text + "- Repeat ratio: "+str(round(repeatRate,1))+" per words"
        labelProgress.set_label(text)

    def SetTitle(self, title, save):

        newTitle = "Perroquet"

        if save:
            newTitle += " *"

        if title != "":
            newTitle += " - " + title

        self.window.set_title(newTitle)

    def SetSequence(self, sequence):
        self.ClearBuffer()
        i = 0
        pos = 1
        cursor_pos = 0

        text = ""
        buffer = self.typeLabel.get_buffer()
        self.AddSymbol(" ")


        for symbol in sequence.GetSymbolList():
            pos += len(symbol)
            self.AddSymbol(symbol)
            if i < len(sequence.GetWordList()):
                if sequence.GetActiveWordIndex() == i:
                    cursor_pos = pos
                if len(sequence.GetWorkList()[i]) == 0:
                    self.AddWordToFound(" ")
                    pos += 1
                elif sequence.GetWordList()[i].lower() == sequence.GetWorkList()[i].lower():

                    self.AddWordFound(sequence.GetWordList()[i])
                    pos += len(sequence.GetWordList()[i])
                else:
                    self.AddWordToFound(sequence.GetWorkList()[i])
                    pos += len(sequence.GetWorkList()[i])
                i += 1

        self.window.set_focus(self.typeLabel)
        newCurPos = cursor_pos + sequence.GetActiveWordPos()
        iter = buffer.get_iter_at_offset(newCurPos)
        buffer.place_cursor(iter)

    def ClearBuffer(self):
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)

        self.currentIndex = 0
        self.currentWordIndex = -1
        self.currentPosIndex = 0
        self.wordIndexMap = []
        self.wordPosMap = []

    def AddSymbol(self, symbol):
        if len(symbol) == 0:
            return
        buffer = self.typeLabel.get_buffer()
        size = buffer.get_char_count()
        iter1 = buffer.get_end_iter()
        buffer.insert(iter1,symbol)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("default", iter1, iter2)

        for i in range(self.currentIndex, self.currentIndex + len(symbol)):
            self.wordIndexMap.append(self.currentWordIndex)
            self.wordPosMap.append(self.currentPosIndex)
        self.currentIndex += len(symbol)

    def AddWordToFound(self, word):
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,word)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_to_found", iter1, iter2)

        self.currentWordIndex += 1
        self.currentPosIndex = 0

        for i in range(self.currentIndex, self.currentIndex + len(word)):
            self.wordIndexMap.append(self.currentWordIndex)
            self.wordPosMap.append(self.currentPosIndex)
            self.currentPosIndex += 1
        self.currentIndex += len(word)

    def AddWordFound(self, word):
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,word)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_found", iter1, iter2)

        self.currentWordIndex += 1
        self.currentPosIndex = 0

        for i in range(self.currentIndex, self.currentIndex + len(word)):
            self.wordIndexMap.append(self.currentWordIndex)
            self.wordPosMap.append(self.currentPosIndex)
            self.currentPosIndex += 1
        self.currentIndex += len(word)

    def initTypeLabel(self):

        buffer = self.typeLabel.get_buffer()

        color_not_found = self.window.get_colormap().alloc_color(0*256, 0*256, 80*256)
        bcolor_not_found = self.window.get_colormap().alloc_color(200*256, 230*256, 250*256)
        color_found = self.window.get_colormap().alloc_color(10*256, 150*256, 10*256)

        buffer.create_tag("default",
             size_points=18.0)
        buffer.create_tag("word_to_found",
             background=bcolor_not_found, foreground=color_not_found, size_points=18.0)
        buffer.create_tag("word_found",
             foreground=color_found, size_points=18.0)


    def on_typeView_key_press_event(self,widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == "Return":
            self.core.UserRepeat()
            self.core.RepeatSequence()
        elif keyname == "space":
            self.core.NextWord()
        elif keyname == "BackSpace":
            self.core.DeletePreviousChar()
        elif keyname == "Delete":
            self.core.DeleteNextChar()
        elif keyname == "Page_Down":
            self.core.PreviousSequence()
        elif keyname == "Page_Up":
            self.core.NextSequence()
        elif keyname == "Right":
            self.core.NextChar()
        elif keyname == "Left":
            self.core.PreviousChar()
        elif keyname == "Home":
            self.core.FirstWord()
        elif keyname == "End":
            self.core.LastWord()
        elif keyname == "F1":
            self.core.CompleteWord()
        elif keyname == "F2":
            toggletoolbuttonShowTranslation = self.builder.get_object("toggletoolbuttonShowTranslation")
            toggletoolbuttonShowTranslation.set_active(not toggletoolbuttonShowTranslation.get_active())
        elif keyname == "Pause":
            self.core.TooglePause()
        else:
            self.core.WriteCharacter(keyname.lower())


        return True;

    def on_toolbuttonNextSequence_clicked(self,widget,data=None):
        self.core.NextSequence()

    def on_toolbuttonPreviousSequence_clicked(self,widget,data=None):
        self.core.PreviousSequence()

    def on_toolbuttonReplaySequence_clicked(self,widget,data=None):
        self.core.UserRepeat()
        self.core.RepeatSequence()

    def on_adjustmentSequenceNum_value_changed(self,widget,data=None):

        value = int(self.builder.get_object("adjustmentSequenceNum").get_value())

        if value != self.settedSeq:
            self.core.SelectSequence(value - 1)

    def on_adjustmentSequenceTime_value_changed(self,widget,data=None):
        value = int(self.builder.get_object("adjustmentSequenceTime").get_value())
        if value != self.settedPos:
            self.core.SeekSequence(value*100)
    def on_toolbuttonHint_clicked(self,widget,data=None):
        self.core.CompleteWord()

    def on_toolbuttonPlay_clicked(self,widget,data=None):
        self.core.Play()

    def on_toolbuttonPause_clicked(self,widget,data=None):
        self.core.Pause()

    def on_saveButton_clicked(self, widget, data=None):
        self.core.Save()

    def on_loadButton_clicked(self, widget, data=None):

        loader = OpenFileSelector(self.window)
        result =loader.run()
        if result == None:
            return

        self.core.LoadExercice(result)

    def AskSavePath(self):

        saver = SaveFileSelector(self.window)
        result =saver.run()
        if result == None:
            return

        path = result

        if path == "None" or path == None :
            path = ""
        elif not path.endswith(".perroquet"):
            path = path +".perroquet"
        return path

    def on_buttonSaveExerciceOk_clicked(self, widget, data=None):
        saveChooser = self.builder.get_object("filechooserdialogSave")
        saveChooser.hide()

    def on_entryFilter_changed(self, widget, data=None):
        self.UpdateWordList()

    def on_toggletoolbuttonShowTranslation_toggled(self, widget, data=None):
        scrolledwindowTranslation = self.builder.get_object("scrolledwindowTranslation")
        if not scrolledwindowTranslation.props.visible:
            scrolledwindowTranslation.show()
        else:
            scrolledwindowTranslation.hide()

    def on_typeView_button_release_event(self, widget, data=None):
        index = self.typeLabel.get_buffer().props.cursor_position

        wordIndex = self.wordIndexMap[index]
        wordIndexPos = self.wordPosMap[index]
        if wordIndex == -1:
            wordIndex = 0
        self.core.SelectSequenceWord(wordIndex,wordIndexPos)
        print "ok2 " + str(wordIndex) + " " + str(wordIndexPos)


    def Activate(self):
        self.builder.get_object("hscaleSequenceNum").set_sensitive(True)
        self.builder.get_object("hscaleSequenceTime").set_sensitive(True)
        self.builder.get_object("toolbuttonHint").set_sensitive(True)
        self.builder.get_object("toolbuttonReplaySequence").set_sensitive(True)

    def Run(self):
        gtk.gdk.threads_init()
        self.window.show()
        gtk.main()

EVENT_FILTER = None

class FileSelector(gtk.FileChooserDialog):
        "A normal file selector"

        def __init__(self, parent, title = None, action = gtk.FILE_CHOOSER_ACTION_OPEN, stockbutton = None):

                if stockbutton is None:
                        if action == gtk.FILE_CHOOSER_ACTION_OPEN:
                                stockbutton = gtk.STOCK_OPEN

                        elif action == gtk.FILE_CHOOSER_ACTION_SAVE:
                                stockbutton = gtk.STOCK_SAVE

                gtk.FileChooserDialog.__init__(
                        self, title, parent, action,
                        ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, stockbutton, gtk.RESPONSE_OK )
                )

                self.set_local_only(False)
                self.set_default_response(gtk.RESPONSE_OK)

                self.inputsection = None


        def add_widget(self, title, widget):
                "Adds a widget to the file selection"

                if self.inputsection == None:
                        self.inputsection = ui.InputSection()
                        self.set_extra_widget(self.inputsection)

                self.inputsection.append_widget(title, widget)


        """def get_filename(self):
                "Returns the file URI"

                uri = self.get_filename()

                if uri == None:
                        return None

                else:
                        return urllib.unquote(uri)"""


        def run(self):
                "Displays and runs the file selector, returns the filename"

                self.show_all()

                if EVENT_FILTER != None:
                        self.window.add_filter(EVENT_FILTER)

                response = gtk.FileChooserDialog.run(self)
                filename = self.get_filename()
                self.destroy()

                if response == gtk.RESPONSE_OK:
                        return filename

                else:
                        return None


class OpenFileSelector(FileSelector):
        "A file selector for opening files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, ('Select File to Open'),
                        gtk.FILE_CHOOSER_ACTION_OPEN, gtk.STOCK_OPEN
                )

                filter = gtk.FileFilter()
                filter.set_name(('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)



class SaveFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, ('Select File to Save to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)
                self.connect("confirm-overwrite", self.__cb_confirm_overwrite)


        def __cb_confirm_overwrite(self, widget, data = None):
                "Handles confirm-overwrite signals"

                try:
                        FileReplace(self, io.file_normpath(self.get_uri())).run()

                except:
                        return gtk.FILE_CHOOSER_CONFIRMATION_SELECT_AGAIN

                else:
                        return gtk.FILE_CHOOSER_CONFIRMATION_ACCEPT_FILENAME



