//
//  Item.swift
//  PiDrums Connect
//
//  Created by Kara Orander on 11/17/25.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
